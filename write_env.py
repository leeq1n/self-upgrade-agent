key = "ms-70be678c-b7de-487a-b806-b5a76c9b22c2"
with open(".env", "w") as f:
    f.write(f"LLM_API_KEY={key}\n")
    f.write("LLM_BASE_URL=https://api-inference.modelscope.cn/v1\n")
    f.write("LLM_MODEL=Qwen/Qwen3.5-35B-A3B\n")
    f.write("LLM_TEMPERATURE=0.1\n")
    f.write("LLM_MAX_TOKENS=2048\n")
print(".env written")
