# Jupyter AI Custom

一个增强版的Jupyter AI扩展，集成了RAG（检索增强生成）系统和公司内部API支持。

## 功能特性

- 🤖 **智能AI助手**: 基于先进的语言模型，提供智能编程辅助
- 📚 **RAG知识检索**: 自动检索公司内部文档和API信息
- 🔧 **公司API集成**: 支持公司内部API函数的自动导入和使用
- 💻 **多语言支持**: 支持Python、SQL、JavaScript等多种编程语言
- 🎯 **专业领域**: 深度支持量化投资、数据分析、机器学习等领域

## 安装方法

### 从whl文件安装

```bash
# 下载whl文件后安装
pip install jupyter_ai_custom-3.0.0b5-py3-none-any.whl

# 或者指定完整路径
pip install /path/to/jupyter_ai_custom-3.0.0b5-py3-none-any.whl
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-company/jupyter-ai-custom.git
cd jupyter-ai-custom

# 安装依赖
pip install -e .
```

## 环境变量配置

在安装后，需要配置以下环境变量：

```bash
# 语言模型配置
set JUPYTER_AI_MODEL_ID=gpt-4o
set JUPYTER_AI_API_BASE=http://your-api-server/llmapi/v1/chat/completions
set JUPYTER_AI_API_KEY=your-api-key

# 嵌入模型配置
set JUPYTER_AI_EMBEDDING_MODEL_ID=Qwen3-Embedding-8B
set JUPYTER_AI_EMBEDDING_API_BASE=http://your-api-server/llmapi/v1/embeddings
set JUPYTER_AI_EMBEDDING_API_KEY=your-api-key

# 编码设置
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
```

## 使用方法

1. 启动JupyterLab
2. 在侧边栏找到AI助手图标
3. 开始与AI助手对话，它会自动：
   - 检索相关文档信息
   - 生成包含正确导入的代码
   - 提供专业的技术建议

## 开发

### 构建whl文件

```bash
# 安装构建工具
pip install build wheel

# 构建whl文件
python -m build

# 构建的文件在 dist/ 目录下
```

### 测试

```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_rag_system.py
```

## 许可证

MIT License

## 支持

如有问题，请联系开发团队或提交Issue。