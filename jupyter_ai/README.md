# Jupyter AI Custom

一个增强版的Jupyter AI扩展，集成了RAG（检索增强生成）系统和公司内部API支持。

## 功能特性

- 🤖 **智能AI助手**: 基于先进的语言模型，提供智能编程辅助
- 📚 **RAG知识检索**: 自动检索公司内部文档和API信息
- 🔧 **公司API集成**: 支持公司内部API函数的自动导入和使用
- 💻 **多语言支持**: 支持Python、SQL、JavaScript等多种编程语言
- 🎯 **专业领域**: 深度支持量化投资、数据分析、机器学习等领域

## 项目结构

```
jupyter_ai/
├── 📁 auth/                    # 身份认证模块
│   └── identity.py             # 用户身份验证和权限管理
├── 📁 completions/             # 代码补全和AI对话处理
│   ├── handlers/               # 补全处理器
│   │   ├── base.py            # 基础处理器接口
│   │   ├── default.py         # 默认补全处理器
│   │   └── model_mixin.py     # 模型混合器
│   └── models.py              # 补全相关数据模型
├── 📁 config/                  # 配置管理
│   └── config_models.py       # 配置数据模型定义
├── 📁 mcp/                     # MCP (Model Context Protocol) 支持
│   ├── mcp_config_loader.py   # MCP配置加载器
│   └── schema.json            # MCP协议模式定义
├── 📁 personas/                # AI人格系统
│   ├── api_knowledge/         # API知识库
│   │   ├── api_schemas.json   # API模式定义
│   │   ├── extra/             # 额外文档资源
│   │   ├── faiss_index.bin    # FAISS向量索引
│   │   └── vector_db.pkl      # 向量数据库
│   ├── company_ai/            # 公司AI人格
│   │   ├── company_ai_persona.py    # 公司AI人格实现
│   │   ├── path_config.py           # 路径配置
│   │   ├── prompt_template.py       # 提示词模板
│   │   ├── rag_manager.py           # RAG管理器
│   │   └── rag_system.py            # RAG检索增强生成系统
│   ├── jupyternaut/           # JupyterNaut人格
│   │   ├── jupyternaut.py     # JupyterNaut核心实现
│   │   └── prompt_template.py # 提示词模板
│   ├── base_persona.py        # 基础人格类
│   ├── persona_manager.py     # 人格管理器
│   └── persona_awareness.py   # 人格感知系统
├── 📁 tools/                   # 工具模块
│   └── models.py              # 工具相关数据模型
├── 📁 tests/                   # 测试模块
│   ├── completions/           # 补全功能测试
│   ├── __snapshots__/         # 测试快照
│   └── test_*.py              # 各种功能测试
├── 📁 static/                  # 静态资源
│   └── jupyternaut.svg        # JupyterNaut图标
├── 🔧 config_manager.py       # 配置管理器
├── 🔧 extension.py            # JupyterLab扩展主入口
├── 🔧 handlers.py             # 事件处理器
├── 🔧 history.py              # 历史记录管理
├── 🔧 models.py               # 核心数据模型
├── 📦 build_whl.py            # 构建脚本
├── 📦 setup.py                # 安装配置
├── 📦 pyproject.toml          # 项目配置
└── 📄 requirements.txt        # 依赖包列表
```

### 核心模块说明

| 模块 | 功能描述 |
|------|----------|
| **auth/** | 用户身份认证和权限管理，确保安全的AI访问 |
| **completions/** | 代码补全和AI对话的核心处理逻辑 |
| **config/** | 系统配置管理，包括模型配置、API配置等 |
| **mcp/** | Model Context Protocol支持，用于模型上下文管理 |
| **personas/** | AI人格系统，包含不同的AI助手角色和知识库 |
| **tools/** | 工具模块，提供各种辅助功能 |
| **tests/** | 完整的测试套件，确保代码质量 |

## 快速开始

### 1. 安装依赖

```bash
# 安装所有依赖包
pip install -r requirements.txt

# 或者从源码安装
pip install -e .
```

### 2. 环境配置

设置必要的环境变量：

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

### 3. 运行示例

```bash
# 启动JupyterLab
jupyter lab

# 打开examples.ipynb查看使用示例
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