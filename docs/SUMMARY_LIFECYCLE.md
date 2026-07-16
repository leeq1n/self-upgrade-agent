# Summary lifecycle (M-task-summary child-summary destroy contract)
Last P20-verified: 2026-07-14 (recursive destroy contract)

> L0: 父任务完成时如何消费 + 销毁子任务总结。
> 递归契约：任意层级都适用（不只 2-3 级）。
> Load when: 父任务有 N>1 子任务完成时；或实现
> M-task-summary 的"汇总 + 清理"循环时；或提交
> 父级 M-task-summary 之前。

## 契约核心（递归销毁）

M-task-summary 完成时（针对有 N 个子任务的父任务），
总结提交必须：

1. **拉取**（Pull）所有 N 个子总结到上下文（来自
   commit message 或 Temp 快照）。缺这一步，父总结
   不完整（per P14 docs-stay-current）。
2. **写入**（Write）父任务自己的总结（per M-task-summary
   规则）。
3. **销毁**（Destroy）所有子总结——**递归销毁**：
   - 若是 Temp 快照总结：在同一个 commit 里
     `git rm` / `os.unlink()`，并在父级 commit
     message 里记录销毁动作。
   - 若是 commit message 总结：用 `git rebase -i`
     把 N 个子 commit **物理销毁**（squash 进父级
     commit）。子 commit message 真的从历史消失。
     父级 commit message 显式记录"consumed +
     destroyed commits c50-c58"。

## 为什么是递归销毁（per P7 奥卡姆）

按 P7 奥卡姆"不要保留冗余状态"：

- 子总结 = 中间状态，不是知识本身
- 知识 = 根节点的总结（祖父级及以上）
- 销毁子树 = P7 的自然推论
- **每升一级都销毁下级** = 任意深度都保持简洁

**可扩展性论证**（per P20 渐进披露 + 你 meta-rule）：

- 2 级任务：1 次父级调用销毁
- 3 级任务：2 次父级调用销毁（3→2→1）
- 4 级任务：3 次父级调用销毁
- N 级任务：N-1 次父级调用销毁
- **任意层都适用**，不只是 L0/L1/L2

## 为什么用 git rebase -i squash（不是"概念销毁"）

旧契约说"destroy = consumed, no longer needed in working set"
（概念上的销毁）。**这是不够的**：

- 概念销毁：子 commit message 仍存在 git 历史
- 物理销毁：子 commit message 真的消失
- **物理销毁 = P7 奥卡姆真执行**（不保留冗余）

`git rebase -i` squash 机制：

- 把 N 个子 commit 压成 1 个父 commit
- 子 commit message 进入父 commit message
- 子 commit 物理消失
- 父 commit message 显式记录"destroyed commits c50-c58"

## 为什么不用 GC（自动垃圾回收）

- 静默删除隐藏工作（违反 P17 老实说）
- GC 可能在父级消费前删除（竞态条件）
- **显式销毁**让"消费-删除"循环成为可审计事件
  （commit message 记录动作）

## P17 与销毁的边界

P17 老实说不等于"不能销毁"。P17 要求：
- 销毁动作在 commit message 里**显式记录**
- 销毁**有意的、可审计的**（不是静默的）
- 销毁在父级 commit message 里说明"为什么销毁 +
  销毁了哪些"

git rebase -i squash 满足 P17：
- 父级 commit message 显式记录"destroyed commits"
- 销毁意图清晰（per M-task-summary 契约）
- 审计追踪通过销毁记录实现

## P7 奥卡姆与销毁的对齐

按 P7 奥卡姆"不要保留冗余状态"：

- 永远保留所有总结 = 文档膨胀
- 子总结是临时状态，不是知识
- 只有父总结（及祖父级以上）进入知识库
- **销毁临时，保留持久**

## 可扩展性（per P20 渐进披露 + 你 meta-rule）

旧契约假设"3 层（L0/L1/L2）"是尽头。**不是**：

- 未来可能有 4 级、5 级、6 级节点
- 旧契约：硬编码 3 层，每多一层要改契约
- 新契约：**递归**——任意层都销毁子级
- 任意深度都保持简洁（per P7 奥卡姆）

## 代码任务的变体

对于带代码的父任务，M-task-summary 只在**联合/集成
测试通过后**触发（per P5 测通）。

- 测试门 = 前置条件
- 销毁 = 后置条件
- **两者都满足**才等于"任务完成"

## 风险与撤销

git rebase -i squash 风险：

- **重写历史**（所有 commit hash 会变）
- 可能丢失子 commit 的独立审计追踪（但父 commit
  message 保留销毁记录）
- 协作环境下需要 force push

撤销方法：

- `git reflog` 找到 rebase 前的状态
- `git reset --hard <reflog-hash>` 撤销
- 在 rebase 前**备份分支**（推荐）

**前置条件**：在 rebase 前**必须**备份分支（per P17
审计追踪 + P25 step 5 风险分析）。

## 与其他规则的关系

- **M-task-summary**（父规则）：触发本契约的规则。
  父级 M-task-summary = N 个子级消费 + 1 个父级
  写入 + N 个子级销毁。
- **M-subtask-summary**（子规则）：产生每个子总结
  的规则（在 commit message 里）。本契约消费
  M-subtask-summary 的输出。
- **M-add-then-reduce**（OPERATING_RULES.md）：包含
  本契约的循环。Add = N 个子 commit + M-subtask-
  summary；Reduce = 父级 M-task-summary + 本销毁契约。
- **P7 奥卡姆**：销毁符合 P7（不保留冗余）。
- **P17 老实说**：销毁在 commit message 里显式记录。
- **P20 渐进披露**：L0/L1/L2 不是尽头，任意层都
  适用。
- **P14 docs-stay-current**：父级消费时确保完整性。

## 实施步骤（git rebase -i squash）

1. **备份分支**：`git branch backup-before-squash-c50-c58`
2. **执行 rebase**：
   ```bash
   git rebase -i <c49-hash>
   # 在编辑器里，把 c50-c58 的 pick 改为 squash
   # （或 s），保留 c59 为父 commit
   ```
3. **编辑 commit message**：把 c59 的 commit message
   加上 "destroyed commits c50-c58" 显式记录
4. **验证**：检查 `git log` 只看到 c59（父级），
   不再看到 c50-c58
5. **force push**（如需要）：`git push --force-with-lease`

## See also

- `docs/OPERATING_RULES.md` — M-task-summary 父规则
- `docs/COMMON_PITFALLS.md` § 3-way table —
  M-task-summary vs M-subtask-summary vs M-learn
- PRINCIPLES.md P17（老实说）— 销毁动作要显式记录
- PRINCIPLES.md P5（测通）— 代码任务测试门
- PRINCIPLES.md P7（奥卡姆）— 销毁的合理性
- PRINCIPLES.md P14（docs stay current）— 父总结完整
- PRINCIPLES.md P20（渐进披露）— 任意层都适用