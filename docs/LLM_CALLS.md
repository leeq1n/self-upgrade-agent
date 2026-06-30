# LLM 调用与多 Key 轮换 (v1.4.0)

本文档说明 self-upgrade-agent 如何调用外部 LLM（默认 ModelScope，
OpenAI-compatible）、如何轮换多个 API key、如何按任务类型路由模型。

## 设计动机

ModelScope 之类的免费推理服务**对每个 API key 有日级调用配额**。
单个 key 一天可能用 50–200 次就到顶。当 key 用尽时，gateway 返回
**HTTP 429** 并附 quota 提示。

为了让 self-upgrade-agent 能在不手动介入的情况下持续运行，我们：

1. **同时配置多个 API key**（`LLM_API_KEY_0` … `LLM_API_KEY_N`），用完一个
   自动换下一个。
2. **按模型也轮换**：每个 key 也会对**特定模型**有日级配额。当一个 key 在
   某个模型上 daily-quota 用尽，**先换 key**（同模型）；**当所有 key 在
   该模型上都被打标记后**，再换下一个模型。
3. **持久化 quota 状态**到 `upgrades/quota_state.json`，避免 daemon
   每天重头开始轮换。

## 轮换策略

```
对每个 model ∈ [primary, *fallback_models]:
    对每个 alive_key ∈ [k0, k1, ..., kN]:
        重试 ≤ max_retries 次（同 key 同 model，分钟级 rate limit）
        ├─ 200 → 成功，返回
        ├─ 429 daily-quota → 标记 key dead_for_today，跳到下一个 key
        ├─ 429 minute-rate-limit → 退避重试
        ├─ 401/403 → 标记 key dead，跳到下一个 key
        ├─ 404 → 模型不可用，跳到下一个 model（保留 key）
        └─ timeout / 5xx → 跳过当前 key

如果所有 key × 所有 model 都失败：返回 error。
```

**关键不变量**：daily-quota 触发后**不退避**，直接切下一个 key——这避免在
已经知道打不动的 key 上空等几十秒。

## 配置 (.env)

```bash
# Multi-key 轮换（按 0..N 顺序）
LLM_API_KEY_0=ms-34dba1e1-...
LLM_API_KEY_1=ms-847a3e57-...
LLM_API_KEY_2=ms-12e76c4b-...
LLM_API_KEY_3=ms-911fd260-...
LLM_API_KEY_4=ms-70be6784-...
LLM_API_KEY_5=ms-c0e91502-...
LLM_API_KEY_6=ms-bdc53351-...

# 如果没有任何 LLM_API_KEY_N，回退到单 key（保持向后兼容）
# LLM_API_KEY=...

# 端点
LLM_BASE_URL=https://api-inference.modelscope.cn/v1
LLM_MODEL=Qwen/Qwen3-Coder-30B-A3B-Instruct

# 调优
LLM_TIMEOUT=60
LLM_MAX_RETRIES=1        # minute-level 429 退避次数
LLM_DAILY_QUOTA_COOLDOWN=86400  # dead key 重新尝试前等多少秒
```

## 按任务类型路由

通过 `LLMConfig.for_task_type(task_type)` 工厂方法选择最适合的模型：

| 任务类型 | 主模型 | 备选 |
|----------|--------|------|
| `code`     | Qwen3-Coder-30B-A3B | DeepSeek-V3.2 → Qwen3-235B → Kimi-K2.5 → GLM-5.1 |
| `reasoning`| DeepSeek-V3.2       | Qwen3-235B → Kimi-K2.5 → GLM-5.1 → Coder-30B |
| `planning` | Qwen3-235B-A22B     | DeepSeek-V3.2 → Kimi-K2.5 → GLM-5.1 → Coder-30B |
| `general`  | Qwen3-Coder-30B-A3B | Qwen3-235B → DeepSeek → Kimi → GLM |

可用 `LLM_MODEL_FOR_CODE=Qwen/Qwen3-...` 等环境变量覆盖主模型；
`LLM_FALLBACK_FOR_CODE=...` 覆盖备选列表（逗号分隔）。

## 调用方怎么用

```python
from src.llm import LLMConfig, chat_simple, quota_snapshot

# 默认（general 任务）
cfg = LLMConfig.from_env()

# 任务路由
cfg = LLMConfig.for_task_type("code")
response = chat_simple("写一个快速排序", config=cfg)

# 查看 quota 状态
print(quota_snapshot())
# → {"ms-34db...": {"dead_until": 0, ...}, "ms-847a...": {"dead_until": 1751347200, ...}}
```

## 故障排查

### "测试 hang 住 / 跑了 3 分钟没结果"

以前是噩梦，现在不会了。每个 LLM 调用有 **两层超时**：

1. **per-request timeout**（`LLM_TIMEOUT`，默认 30s）—— 单次 HTTP 请求上限
2. **total_timeout**（`LLM_TOTAL_TIMEOUT`，默认 60s）—— 整个 `chat()` 调用上限（跨所有 key × model）

如果 total_timeout 被触发或所有 key/model 都失败，函数会：
- **默认**：返回 `LLMResponse(content="", error="...", diagnostic={...})` —— `diagnostic` 字段是结构化报告
- **`raise_on_timeout=True`**：抛 `LLMCallTimeout` 异常，`.report` 字段同样是结构化报告

`diagnose()` 一行命令输出当前 LLM 配置 + quota 状态（key 会被 redact）。

```python
from src.llm import diagnose, chat, LLMConfig
print(diagnose())
# {
#   "ready": true,
#   "base_url": "https://api-inference.modelscope.cn/v1",
#   "primary_model": "Qwen/Qwen3.5-2B",
#   "fallback_count": 8,
#   "api_key_count": 7,
#   "api_keys_redacted": ["key#0:ms-34d...5825", ...],
#   "quota": {...},
#   "total_timeout_s": 60.0,
#   "per_request_timeout_s": 30,
# }
```

### 详细诊断报告（`diagnostic` / `report` 字段）

每次 LLM 调用返回的 `LLMResponse.diagnostic`（或 `LLMCallTimeout.report`）包含：

```python
{
  "total_timeout": 60.0,
  "total_elapsed_s": 23.4,
  "attempts": 7,
  "last_error": "daily_quota_dead on Qwen3.5-2B",
  "tried": [
    {"model": "Qwen3.5-2B", "key_index": 0, "status": 429,
     "elapsed_s": 1.2, "note": "daily_quota_dead"},
    {"model": "Qwen3.5-2B", "key_index": 1, "status": 429,
     "elapsed_s": 0.3, "note": "daily_quota_dead"},
    ...
  ],
  "quota_snapshot": {"ms-34d...": {"dead_until": 1782897123, ...}, ...},
  "models_attempted": ["Qwen3.5-2B", "Qwen2.5-3B-Instruct", ...],
}
```

`note` 字段解释每次失败的原因：`daily_quota_dead` / `rate_limited_retries_exhausted` /
`model_not_found` / `auth_failed_marked_dead` / `httpx_timeout` / `http_500` 等。

### 其他问题

- **所有调用都 429**：检查 `upgrades/quota_state.json`——可能所有 key
  都被标记 dead。等 `LLM_DAILY_QUOTA_COOLDOWN` 秒或手动清空该文件。
- **"LLM not configured"**：`.env` 里没有 `LLM_API_KEY_*` 也没有
  `LLM_API_KEY`。`run.py` 会在启动时自动加载 `.env`。
- **测试 hang 住**：以前 `pytest tests/ -q` 会因为 LLM 限流跑 200s+。
  现在 conftest.py 默认会 (a) 无 key 时 auto-skip `@pytest.mark.llm` 测试，
  (b) 用 `Qwen3.5-2B` 这种便宜模型，(c) 设 `LLM_TOTAL_TIMEOUT=20s`。
  整个测试套件最多 2s（纯逻辑）+ 30-60s（含 LLM）跑完。

## 为什么不做"每天自动重置"

我们的 `upgrades/quota_state.json` 用 `dead_until = now + cooldown`
标记 dead，**到时间自动清零**——这等价于"明天重试"。但 day boundary
并不严格匹配 ModelScope 的 quota 周期（可能 UTC 0 点或别的时间），所以
dead 标记**只是当前进程内的最优近似**。如果发现 ModelScope 实际已经
放开但我们还在等 cooldown，把 `LLM_DAILY_QUOTA_COOLDOWN` 调小即可。
