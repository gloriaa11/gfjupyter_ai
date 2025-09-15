# Jupyter AI Environment Variables Configuration

This document describes the environment variables used by Jupyter AI for API configuration.

## Required Environment Variables

### Model Configuration
- `JUPYTER_AI_MODEL_ID`: The model ID to use for chat completions (default: "gpt-4o")
- `JUPYTER_AI_API_BASE`: The API base URL for chat completions (default: "http://ai.gffunds.com.cn/llmapi/v1/chat/completions")
- `JUPYTER_AI_API_KEY`: The API key for chat completions (required)

### Embedding Configuration
- `JUPYTER_AI_EMBEDDING_MODEL_ID`: The model ID to use for embeddings (default: "Qwen3-Embedding-8B")
- `JUPYTER_AI_EMBEDDING_API_BASE`: The API base URL for embeddings (default: "http://10.89.188.246:8000/llmapi/v1/embeddings")
- `JUPYTER_AI_EMBEDDING_API_KEY`: The API key for embeddings (required)

### Python Configuration
- `PYTHONIOENCODING`: Set to "utf-8" for proper Unicode handling
- `PYTHONUTF8`: Set to "1" to enable UTF-8 mode

## Example Configuration

### Windows (Command Prompt)
```cmd
set JUPYTER_AI_MODEL_ID=gpt-4o
set JUPYTER_AI_API_BASE=http://ai.gffunds.com.cn/llmapi/v1/chat/completions
set JUPYTER_AI_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
set JUPYTER_AI_EMBEDDING_MODEL_ID=Qwen3-Embedding-8B
set JUPYTER_AI_EMBEDDING_API_BASE=http://10.89.188.246:8000/llmapi/v1/embeddings
set JUPYTER_AI_EMBEDDING_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
```

### Windows (PowerShell)
```powershell
$env:JUPYTER_AI_MODEL_ID="gpt-4o"
$env:JUPYTER_AI_API_BASE="http://ai.gffunds.com.cn/llmapi/v1/chat/completions"
$env:JUPYTER_AI_API_KEY="2ce9ab1ea7e84dd2aa7b35bc83df9b27"
$env:JUPYTER_AI_EMBEDDING_MODEL_ID="Qwen3-Embedding-8B"
$env:JUPYTER_AI_EMBEDDING_API_BASE="http://ai.gffunds.com.cn/llmapi/v1/embedding"
$env:JUPYTER_AI_EMBEDDING_API_KEY="2ce9ab1ea7e84dd2aa7b35bc83df9b27"
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
```

### Linux/macOS
```bash
export JUPYTER_AI_MODEL_ID=gpt-4o
export JUPYTER_AI_API_BASE=http://ai.gffunds.com.cn/llmapi/v1/chat/completions
export JUPYTER_AI_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
export JUPYTER_AI_EMBEDDING_MODEL_ID=Qwen3-Embedding-8B
export JUPYTER_AI_EMBEDDING_API_BASE=http://10.89.188.246:8000/llmapi/v1/embeddings
export JUPYTER_AI_EMBEDDING_API_KEY=2ce9ab1ea7e84dd2aa7b35bc83df9b27
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
```

## Fallback Behavior

If environment variables are not set, the system will fall back to the hardcoded default values. However, it is recommended to set all required environment variables for proper configuration management.

## Security Notes

- Never commit API keys to version control
- Use environment variables or secure configuration management systems
- Consider using `.env` files for local development (not included in this project)
- Rotate API keys regularly

## Migration from Hardcoded Values

The following hardcoded values have been replaced with environment variables:

### Previously Hardcoded in `personas/jupyternaut/jupyternaut.py`:
- API base URL: `"http://ai.gffunds.com.cn/llmapi/v1"` → `JUPYTER_AI_API_BASE`
- Model ID: `"gpt-4o"` → `JUPYTER_AI_MODEL_ID`

### Previously Hardcoded in `personas/company_ai/rag_system.py`:
- Embedding API URL: `"http://ai.gffunds.com.cn/llmapi/v1/embeddings"` → `JUPYTER_AI_EMBEDDING_API_BASE`
- API Key: `"2ce9ab1ea7e84dd2aa7b35bc83df9b27"` → `JUPYTER_AI_EMBEDDING_API_KEY`
- Embedding Model: `"Qwen3-Embedding-8B"` → `JUPYTER_AI_EMBEDDING_MODEL_ID`
- Fallback Models: `["text2vec-large-chinese-m", "text-embedding-3-large"]` → Configurable via environment