@echo off
echo 设置Jupyter AI环境变量...
set JUPYTER_AI_MODEL_ID=gpt-4o
set JUPYTER_AI_API_BASE=http://10.89.188.246:8000/llmapi/v1/chat/completions
set JUPYTER_AI_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
set JUPYTER_AI_EMBEDDING_MODEL_ID=Qwen3-Embedding-8B
set JUPYTER_AI_EMBEDDING_API_BASE=http://10.89.188.246:8000/llmapi/v1/embedding
set JUPYTER_AI_EMBEDDING_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
echo 环境变量设置完成！
echo 启动Jupyter Lab...
jupyter lab
