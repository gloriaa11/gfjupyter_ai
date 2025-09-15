"""
Environment variable configuration utility for Jupyter AI personas.
This module provides functions to read API configuration from environment variables
with proper fallbacks and validation.
"""

import os
from typing import Optional, List


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default value and required validation.
    
    Args:
        key: Environment variable name
        default: Default value if environment variable is not set
        required: If True, raise ValueError when environment variable is not set
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required=True and environment variable is not set
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def get_model_config() -> dict:
    """
    Get model configuration from environment variables.
    
    Returns:
        Dictionary containing model configuration
    """
    model_id = get_env_var("JUPYTER_AI_MODEL_ID", "gpt-4o")
    api_base = get_env_var("JUPYTER_AI_API_BASE", "http://10.89.188.246:8000/llmapi/v1/chat/completions")
    api_key = get_env_var("JUPYTER_AI_API_KEY", "2ce9ab1ea7e84dd2aa7b35bc83df9b27")
    
    # 调试信息
    print(f"🔍 DEBUG: 环境变量读取 - MODEL_ID: {model_id}")
    print(f"🔍 DEBUG: 环境变量读取 - API_BASE: {api_base}")
    print(f"🔍 DEBUG: 环境变量读取 - API_KEY: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    
    return {
        "model_id": model_id,
        "api_base": api_base,
        "api_key": api_key,
    }


def get_embedding_config() -> dict:
    """
    Get embedding configuration from environment variables.
    
    Returns:
        Dictionary containing embedding configuration
    """
    return {
        "api_base": get_env_var("JUPYTER_AI_EMBEDDING_API_BASE", "http://10.89.188.246:8000/llmapi/v1/embeddings"),
        "api_key": get_env_var("JUPYTER_AI_EMBEDDING_API_KEY", "2ce9ab1ea7e84dd2aa7b35bc83df9b27"),
        "model_id": get_env_var("JUPYTER_AI_EMBEDDING_MODEL_ID", "Qwen3-Embedding-8B"),
    }


def get_embedding_model_priority_list() -> List[str]:
    """
    Get list of embedding models to try in priority order.
    
    Returns:
        List of model names in priority order
    """
    primary_model = get_env_var("JUPYTER_AI_EMBEDDING_MODEL_ID", "Qwen3-Embedding-8B")
    fallback_models = [
        "text2vec-large-chinese-m",
        "text-embedding-3-large"
    ]
    
    # Remove primary model from fallback list if it's already there
    if primary_model in fallback_models:
        fallback_models.remove(primary_model)
    
    return [primary_model] + fallback_models


def validate_config() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If required configuration is missing
    """
    # Check required variables
    required_vars = [
        "JUPYTER_AI_API_KEY",
        "JUPYTER_AI_EMBEDDING_API_KEY"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable '{var}' is not set")
    
    return True