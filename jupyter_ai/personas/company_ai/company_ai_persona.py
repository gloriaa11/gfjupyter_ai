import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jupyterlab_chat.models import Message
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...history import YChatHistory
from ..base_persona import BasePersona, PersonaDefaults
from .prompt_template import COMPANY_AI_PROMPT_TEMPLATE, CompanyAIVariables
from .rag_system import RAGSystem
from .path_config import get_api_schemas_path


class CompanyAIPersona(BasePersona):
    """
    增强版的Company AI Persona，使用RAG系统实现真正的文档记忆和检索功能。
    能够自动记忆公司内部包和API，并根据用户问题智能检索相关文档。
    """

    def __init__(self, ychat=None, config_manager=None, message_interrupted=None, **kwargs):
        super().__init__(ychat=ychat, config_manager=config_manager, message_interrupted=message_interrupted, **kwargs)
        self._rag_system = None
        self._initialize_rag_system()

    @property
    def defaults(self):
        return PersonaDefaults(
            name="Company AI",
            avatar_path="/api/ai/static/jupyternaut.svg",  # 可以替换为公司logo
            description="增强版AI助手，使用RAG技术自动记忆公司内部包和API，能够智能检索相关文档并回答问题。",
            system_prompt="...",
        )

    def _initialize_rag_system(self):
        """初始化RAG系统"""
        try:
            # 使用硬编码路径
            import sys
            project_root = r"C:\Users\dc-develop-2\Desktop\work\pre\code\jupyter-ai\jupyter-ai\packages\jupyter-ai"
            sys.path.insert(0, project_root)
            
            # 尝试初始化RAG系统
            from .rag_system import RAGSystem
            self._rag_system = RAGSystem()
            self.log.info("RAG系统初始化成功")
        except ImportError as e:
            self.log.warning(f"RAG系统初始化失败，缺少依赖: {e}")
            self.log.warning("请安装必要的依赖: pip install sentence-transformers faiss-cpu numpy")
            self._rag_system = None
        except Exception as e:
            self.log.error(f"RAG系统初始化失败: {e}")
            self._rag_system = None

    def _get_relevant_context(self, user_message: str) -> str:
        """使用RAG系统获取相关的上下文信息"""
        if not self._rag_system:
            return self._get_fallback_context(user_message)
        
        try:
            # 使用RAG系统搜索相关文档
            search_results = self._rag_system.search(user_message, top_k=5)
            
            if not search_results:
                return "未找到相关的文档信息。"
            
            # 格式化搜索结果
            context_parts = ["## 相关文档信息\n"]
            
            for i, result in enumerate(search_results, 1):
                context_parts.append(f"### {i}. {result['title']}")
                context_parts.append(f"**相似度**: {result['similarity_score']:.3f}")
                context_parts.append(f"**类型**: {result.get('type', 'unknown')}")
                
                if result.get('type') == 'api_function':
                    metadata = result.get('metadata', {})
                    context_parts.append(f"**函数名**: {metadata.get('name', 'Unknown')}")
                    context_parts.append(f"**描述**: {metadata.get('description', 'No description')}")
                    
                    params = metadata.get("parameters", {})
                    if params.get("properties"):
                        context_parts.append("**参数**:")
                        for param_name, param_info in params["properties"].items():
                            param_desc = param_info.get("description", "")
                            context_parts.append(f"  - `{param_name}`: {param_desc}")
                
                elif result.get('type') == 'api_class':
                    metadata = result.get('metadata', {})
                    context_parts.append(f"**类名**: {metadata.get('name', 'Unknown')}")
                    context_parts.append(f"**描述**: {metadata.get('description', 'No description')}")
                    
                    methods = metadata.get("methods", [])
                    if methods:
                        context_parts.append("**方法**:")
                        for method in methods[:5]:  # 限制显示数量
                            method_name = method.get("name", "Unknown")
                            method_desc = method.get("description", "")
                            context_parts.append(f"  - `{method_name}`: {method_desc}")
                
                else:  # document type
                    context_parts.append(f"**来源**: {result.get('source_file', 'Unknown')}")
                
                context_parts.append(f"**内容**:\n{result['content']}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.log.error(f"RAG搜索失败: {e}")
            return self._get_fallback_context(user_message)

    def _get_fallback_context(self, user_message: str) -> str:
        """备用上下文获取方法（当RAG系统不可用时）"""
        context_parts = []
        
        # 尝试加载API schemas
        try:
            api_schemas_path = get_api_schemas_path()
            if api_schemas_path.exists():
                with open(api_schemas_path, 'r', encoding='utf-8') as f:
                    api_knowledge = json.load(f)
                
                # 根据用户消息筛选相关API
                user_lower = user_message.lower()
                relevant_apis = []
                
                for item in api_knowledge:
                    if item.get("type") == "function":
                        name = item.get("name", "").lower()
                        desc = item.get("description", "").lower()
                        
                        # 检查是否与用户问题相关
                        if any(keyword in name or keyword in desc for keyword in user_lower.split()):
                            relevant_apis.append(item)
                
                if relevant_apis:
                    context_parts.append("## 相关API函数\n")
                    for api in relevant_apis[:5]:  # 限制数量
                        context_parts.append(f"**{api.get('name')}**")
                        context_parts.append(f"- 描述: {api.get('description', 'No description')}")
                        
                        params = api.get("parameters", {})
                        if params.get("properties"):
                            context_parts.append("- 参数:")
                            for param_name, param_info in params["properties"].items():
                                param_desc = param_info.get("description", "")
                                context_parts.append(f"  - `{param_name}`: {param_desc}")
                        context_parts.append("")
                
        except Exception as e:
            self.log.error(f"加载API schemas失败: {e}")
        
        # 尝试加载公司文档
        try:
            extra_dir = Path("extra")
            if extra_dir.exists():
                # 根据用户消息关键词搜索文档
                user_keywords = set(user_lower.split())
                relevant_docs = []
                
                for doc_file in extra_dir.glob("*.txt"):
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            
                            # 计算相关性分数
                            relevance_score = sum(1 for keyword in user_keywords if keyword in content)
                            if relevance_score > 0:
                                relevant_docs.append((doc_file.stem, content, relevance_score))
                    except Exception as e:
                        continue
                
                # 按相关性排序
                relevant_docs.sort(key=lambda x: x[2], reverse=True)
                
                if relevant_docs:
                    context_parts.append("## 相关文档\n")
                    for title, content, score in relevant_docs[:3]:  # 限制数量
                        summary = content[:300] + "..." if len(content) > 300 else content
                        context_parts.append(f"**{title}** (相关性: {score})")
                        context_parts.append(f"{summary}\n")
                
        except Exception as e:
            self.log.error(f"加载公司文档失败: {e}")
        
        if not context_parts:
            return "无法获取相关上下文信息。"
        
        return "\n".join(context_parts)

    async def process_message(self, message: Message) -> None:
        # 直接使用我们的API客户端，而不是Jupyter AI的默认配置
        try:
            # 导入我们的API客户端
            import sys
            project_root = r"C:\Users\dc-develop-2\Desktop\work\pre\code\jupyter-ai\jupyter-ai"
            sys.path.insert(0, project_root)
            
            from llm_client import LLMClient
            from api_config import API_KEY
            
            # 初始化API客户端
            llm_client = LLMClient(api_key=API_KEY)
            
            # 获取公司内部知识库上下文（使用RAG系统）
            company_context = self._get_relevant_context(message.body)
            
            # 构建完整的提示
            system_prompt = """你是一个专业的AI助手，专门用于回答基于公司内部文档和API的问题。
请根据提供的上下文信息，准确、详细地回答用户的问题。
如果上下文中没有相关信息，请明确说明。"""
            
            full_prompt = f"{system_prompt}\n\n## 相关上下文信息\n{company_context}\n\n## 用户问题\n{message.body}\n\n## 回答"
            
            # 使用API客户端发送请求
            try:
                response = llm_client.chat(full_prompt)
                self.send_message(response)
            except Exception as e:
                error_msg = f"API调用失败: {e}"
                self.log.error(error_msg)
                self.send_message(f"抱歉，API调用失败: {e}")
                
        except Exception as e:
            error_msg = f"处理消息失败: {e}"
            self.log.error(error_msg)
            self.send_message(f"抱歉，处理消息时出现错误: {e}")

    def build_runnable(self) -> Any:
        llm = self.config_manager.lm_provider(**self.config_manager.lm_provider_params)
        print(f"实际访问{llm.client.base_url}")
        runnable = COMPANY_AI_PROMPT_TEMPLATE | llm | StrOutputParser()

        runnable = RunnableWithMessageHistory(
            runnable=runnable,
            get_session_history=lambda: YChatHistory(ychat=self.ychat, k=2),
            input_messages_key="input",
            history_messages_key="history",
        )

        return runnable 

    def get_knowledge_summary(self) -> str:
        """获取知识库摘要"""
        if self._rag_system:
            return self._rag_system.get_knowledge_summary()
        else:
            return "RAG系统未初始化，无法获取知识库摘要。"

    def update_knowledge_base(self) -> str:
        """更新知识库"""
        if self._rag_system:
            try:
                self._rag_system.update_knowledge_base()
                return "知识库更新成功！"
            except Exception as e:
                return f"知识库更新失败: {e}"
        else:
            return "RAG系统未初始化，无法更新知识库。" 