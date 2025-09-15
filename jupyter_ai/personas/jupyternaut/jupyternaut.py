# from typing import Any

# from jupyterlab_chat.models import Message
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables.history import RunnableWithMessageHistory

# from ...history import YChatHistory
# from ..base_persona import BasePersona, PersonaDefaults
# from .prompt_template import JUPYTERNAUT_PROMPT_TEMPLATE, JupyternautVariables
# import os
# from ..company_ai.rag_system import RAGSystem
# class JupyternautPersona(BasePersona):
#     """
#     The Jupyternaut persona, the main persona provided by Jupyter AI.
#     """
    
#     print("🔧 DEBUG: JupyternautPersona 类被加载")

#     def __init__(self, *args, **kwargs):
#         print("🚀 DEBUG: JupyternautPersona.__init__ 被调用")
#         print(f"🔧 DEBUG: 参数: args={args}, kwargs={kwargs}")
#         super().__init__(*args, **kwargs)
#         print("✅ DEBUG: JupyternautPersona.__init__ 完成")

#     @property
#     def defaults(self):
#         return PersonaDefaults(
#             name="Jupyternaut",
#             avatar_path="/api/ai/static/jupyternaut.svg",
#             description="The standard agent provided by JupyterLab. Currently has no tools.",
#             system_prompt="...",
#         )
#     import os
#     def _initialize_rag_system(self):
#         try:
#             self._rag_system = RAGSystem()
#             print("[DEBUG] RAGSystem 初始化成功")
#         except Exception as e:
#             print(f"[DEBUG] RAGSystem 初始化失败: {e}")
#             self._rag_system = None

#     def get_rag_context(self, query: str) -> str:
#         if not hasattr(self, '_rag_system') or self._rag_system is None:
#             self._initialize_rag_system()
#         if not self._rag_system:
#             return f"RAG系统不可用，无法检索 '{query}' 的相关内容。"
#         try:
#             search_results = self._rag_system.search(query, top_k=5)
#             if not search_results:
#                 return f"未找到 '{query}' 的相关文档信息。"
#             context_parts = ["## 相关文档信息\n"]
#             for i, result in enumerate(search_results, 1):
#                 context_parts.append(f"### {i}. {result.get('title', '无标题')}")
#                 context_parts.append(f"**相似度**: {result.get('similarity_score', 0):.3f}")
#                 context_parts.append(f"**内容**:\n{result.get('content', '')}\n")
#             return "\n".join(context_parts)
#         except Exception as e:
#             print(f"[DEBUG] RAG 检索异常: {e}")
#             return f"RAG检索异常: {e}"

#     async def process_message(self, message: Message) -> None:
#         print("=" * 80)
#         print("🚀🚀🚀 JUPYTERNAUT PROCESS_MESSAGE 开始执行 🚀🚀🚀")
#         print("=" * 80)
#         print("🚀 DEBUG: process_message 开始执行")
#         print(f"🔍 DEBUG: 收到消息: {message.body}")
        
#         # 先发送一个测试消息确认代码执行
#         self.send_message("🔧 调试：JupyternautPersona.process_message 正在执行...")
        
#         if not self.config_manager.lm_provider:
#             print("❌ DEBUG: 没有配置语言模型提供者")
#             self.send_message(
#                 "No language model provider configured. Please set one in the Jupyter AI settings."
#             )
#             return

#         provider_name = self.config_manager.lm_provider.name
#         model_id = self.config_manager.lm_provider_params["model_id"]
#         print(f"🔧 DEBUG: 使用提供者: {provider_name}, 模型: {model_id}")
#         print(f"🔧 DEBUG: 提供者参数: {self.config_manager.lm_provider_params}")
        
#         # 发送配置信息确认
#         self.send_message(f"🔧 配置确认：提供者={provider_name}, 模型={model_id}")



#         rag_context = self.get_rag_context(message.body)
#        # print(f"[DEBUG] RAG 检索结果: {rag_context}")

#         # Process file attachments and include their content in the context
#         attach_context = self.process_attachments(message)
#         print(f"📎 DEBUG: 附件处理后的上下文长度: {len(attach_context) if attach_context else 0}")

#         # 合并 RAG 检索和附件内容
#         if attach_context:
#             context = rag_context + "\n" + attach_context
#         else:
#             context = rag_context
#         print(f"[DEBUG] 最终 context: {context}")

#         print("🔨 DEBUG: 开始构建 runnable...")
#         try:
#             runnable = self.build_runnable()
#             print(f"✅ DEBUG: runnable 构建完成，类型: {type(runnable)}")
#             self.send_message("🔧 runnable 构建成功")
#         except Exception as e:
#             print(f"❌ DEBUG: runnable 构建失败: {e}")
#             self.send_message(f"❌ runnable 构建失败: {e}")
#             return
        
#         variables = JupyternautVariables(
#             input=message.body,
#             model_id=model_id,
#             provider_name=provider_name,
#             persona_name=self.name,
#             context=context,
#         )
#         variables_dict = variables.model_dump()
#         print(f"📝 DEBUG: 变量准备完成: {variables_dict}")
#         reply_stream=runnable.astream(variables_dict)
#         await self.stream_message(reply_stream)


#     def build_runnable(self) -> Any:
#         print("🔨 DEBUG: build_runnable 开始执行")
        
#         # TODO: support model parameters. maybe we just add it to lm_provider_params in both 2.x and 3.x
#         print("🔧 DEBUG: 创建语言模型实例...")
#         try:
#             llm = self.config_manager.lm_provider(**self.config_manager.lm_provider_params)
#             print(f"✅ DEBUG: 语言模型创建成功，类型: {type(llm)}")
#             print(f"🔧 DEBUG: LLM 实例: {llm}")
#         except Exception as e:
#             print(f"❌ DEBUG: 语言模型创建失败: {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise
        
#         print("🔧 DEBUG: 构建基础链...")
#         try:
#             # 简化链构建，先测试基本功能
#             runnable = JUPYTERNAUT_PROMPT_TEMPLATE | llm | StrOutputParser()
#             print(f"✅ DEBUG: 基础链构建成功，类型: {type(runnable)}")
#             print(f"🔧 DEBUG: 基础链: {runnable}")
#         except Exception as e:
#             print(f"❌ DEBUG: 基础链构建失败: {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("🔧 DEBUG: 添加消息历史支持...")
#         try:
#             runnable = RunnableWithMessageHistory(
#                 runnable=runnable,  #  type:ignore[arg-type]
#                 get_session_history=lambda: YChatHistory(ychat=self.ychat, k=2),
#                 input_messages_key="input",
#                 history_messages_key="history",
#             )
#             print(f"✅ DEBUG: 消息历史支持添加成功，类型: {type(runnable)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 消息历史支持添加失败: {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("✅ DEBUG: build_runnable 完成")
#         return runnable
from typing import Any

from jupyterlab_chat.models import Message
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...history import YChatHistory
from ..base_persona import BasePersona, PersonaDefaults
from .prompt_template import JUPYTERNAUT_PROMPT_TEMPLATE, JupyternautVariables
import os
from ..company_ai.rag_system import RAGSystem

# class JupyternautPersona(BasePersona):
#     """
#     The Jupyternaut persona, the main persona provided by Jupyter AI.
#     """
    
#     print("🔧 DEBUG: JupyternautPersona 类被加载")

#     def __init__(self, *args, **kwargs):
#         print("🚀 DEBUG: JupyternautPersona.__init__ 被调用")
#         print(f"🔧 DEBUG: 参数: args={args}, kwargs={kwargs}")
#         super().__init__(*args, **kwargs)
#         print("✅ DEBUG: JupyternautPersona.__init__ 完成")

#     @property
#     def defaults(self):
#         return PersonaDefaults(
#             name="Jupyternaut",
#             avatar_path="/api/ai/static/jupyternaut.svg",
#             description="The standard agent provided by JupyterLab. Currently has no tools.",
#             system_prompt="...",
#         )

#     def _initialize_rag_system(self):
#         print("🔧 DEBUG: _initialize_rag_system 开始执行")
#         try:
#             self._rag_system = RAGSystem()
#             print("[DEBUG] RAGSystem 初始化成功")
#         except Exception as e:
#             print(f"[DEBUG] RAGSystem 初始化失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] RAGSystem 初始化错误堆栈: {traceback.format_exc()}")
#             self._rag_system = None

#     def get_rag_context(self, query: str) -> str:
#         print(f"🔍 DEBUG: get_rag_context 开始执行，查询: {query}")
#         if not hasattr(self, '_rag_system') or self._rag_system is None:
#             print("[DEBUG] RAGSystem 未初始化，尝试初始化")
#             self._initialize_rag_system()
#         if not self._rag_system:
#             print("[DEBUG] RAGSystem 不可用")
#             return f"RAG系统不可用，无法检索 '{query}' 的相关内容。"
#         try:
#             print("[DEBUG] 开始 RAG 检索...")
#             search_results = self._rag_system.search(query, top_k=3)
#             print(f"[DEBUG] RAG 检索结果数量: {len(search_results) if search_results else 0}")
#             if not search_results:
#                 print(f"[DEBUG] 未找到 '{query}' 的相关文档")
#                 return f"未找到 '{query}' 的相关文档信息。"
#             context_parts = ["## 相关文档信息\n"]
#             for i, result in enumerate(search_results, 1):
#                 print(f"[DEBUG] 处理 RAG 结果 {i}: 标题={result.get('title', '无标题')}, 相似度={result.get('similarity_score', 0):.3f}")
#                 context_parts.append(f"### {i}. {result.get('title', '无标题')}")
#                 context_parts.append(f"**相似度**: {result.get('similarity_score', 0):.3f}")
#                 context_parts.append(f"**内容**:\n{result.get('content', '')}\n")
#             context = "\n".join(context_parts)
#             print(f"[DEBUG] RAG 上下文生成完成，长度: {len(context)} 字符")
#             return context
#         except Exception as e:
#             print(f"[DEBUG] RAG 检索异常: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] RAG 检索错误堆栈: {traceback.format_exc()}")
#             return f"RAG检索异常: {e}"

#     async def process_message(self, message: Message) -> None:
#         print("=" * 80)
#         print("🚀🚀🚀 JUPYTERNAUT PROCESS_MESSAGE 开始执行 🚀🚀🚀")
#         print("=" * 80)
#         print("🚀 DEBUG: process_message 开始执行")
#         print(f"🔍 DEBUG: 收到消息: {message.body}")
#         print(f"🔍 DEBUG: 消息对象: {repr(message)}")
        
#         # 先发送一个测试消息确认代码执行
#         self.send_message("🔧 调试：JupyternautPersona.process_message 正在执行...")
        
#         if not self.config_manager.lm_provider:
#             print("❌ DEBUG: 没有配置语言模型提供者")
#             self.send_message(
#                 "No language model provider configured. Please set one in the Jupyter AI settings."
#             )
#             return

#         provider_name = self.config_manager.lm_provider.name
#         model_id = self.config_manager.lm_provider_params["model_id"]
#         print(f"🔧 DEBUG: 使用提供者: {provider_name}, 模型: {model_id}")
#         print(f"🔧 DEBUG: 提供者参数: {self.config_manager.lm_provider_params}")
        
#         # 发送配置信息确认
#         self.send_message(f"🔧 配置确认：提供者={provider_name}, 模型={model_id}")

#         print("🔍 DEBUG: 开始获取 RAG 上下文")
#         rag_context = self.get_rag_context(message.body)
#         print(f"[DEBUG] RAG 检索结果长度: {len(rag_context)} 字符")
#        # print(f"[DEBUG] RAG 检索结果 (前500字符): {rag_context[:500]}...")

#         # Process file attachments and include their content in the context
#         print("📎 DEBUG: 开始处理附件")
#         attach_context = self.process_attachments(message)
#         print(f"📎 DEBUG: 附件处理后的上下文长度: {len(attach_context) if attach_context else 0}")
#         if attach_context:
#             print(f"📎 DEBUG: 附件上下文 (前500字符): {attach_context[:500]}...")

#         # 合并 RAG 检索和附件内容
#         if attach_context:
#             context = rag_context + "\n" + attach_context
#         else:
#             context = rag_context
#         print(f"[DEBUG] 最终合并上下文长度: {len(context)} 字符")
#         print(f"[DEBUG] 最终合并上下文 (前500字符): {context[:500]}...")

#         print("🔨 DEBUG: 开始构建 runnable...")
#         try:
#             runnable = self.build_runnable()
#             print(f"✅ DEBUG: runnable 构建完成，类型: {type(runnable)}")
#             self.send_message("🔧 runnable 构建成功")
#         except Exception as e:
#             print(f"❌ DEBUG: runnable 构建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: runnable 构建错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ runnable 构建失败: {e}")
#             return
        
#         variables = JupyternautVariables(
#             input=message.body,
#             model_id=model_id,
#             provider_name=provider_name,
#             persona_name=self.name,
#             context=context,
#         )
#         variables_dict = variables.model_dump()
#         print(f"📝 DEBUG: 变量准备完成: {variables_dict}")
#         print(f"📝 DEBUG: 变量字典键: {list(variables_dict.keys())}")
#         print(f"📝 DEBUG: 输入内容长度: {len(variables_dict.get('input', ''))} 字符")
#         print(f"📝 DEBUG: 上下文内容长度: {len(variables_dict.get('context', ''))} 字符")
#         print("🔍 DEBUG: 测试同步调用 runnable.invoke...")
#         try:
#             sync_result = await runnable.invoke(variables_dict)
#             print(f"[DEBUG] 同步调用结果: {sync_result}")
#             self.send_message(f"🔧 同步调用结果: {sync_result}")
#         except Exception as e:
#             print(f"[DEBUG] 同步调用失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] 同步调用错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ 同步调用失败: {e}")
#             return
#         print("🔄 DEBUG: 开始创建 reply_stream...")
#         try:
#             reply_stream = runnable.astream(variables_dict)
#             print(f"✅ DEBUG: reply_stream 创建成功，类型: {type(reply_stream)}")
#             print(f"🔍 DEBUG: reply_stream 对象: {repr(reply_stream)}")
#         except Exception as e:
#             print(f"❌ DEBUG: reply_stream 创建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: reply_stream 创建错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ reply_stream 创建失败: {e}")
#             return

#         # 手动测试 reply_stream
#         print("🔍 DEBUG: 手动测试 reply_stream...")
#         try:
#             agen = reply_stream.__aiter__()
#             for i in range(5):
#                 try:
#                     chunk = await agen.__anext__()
#                     print(f"[DEBUG] reply_stream 手动产出 chunk[{i}]: {chunk}")
#                 except StopAsyncIteration:
#                     print(f"[DEBUG] reply_stream 手动产出 StopAsyncIteration at {i}")
#                     break
#                 except Exception as e:
#                     print(f"[DEBUG] reply_stream 手动产出异常: {type(e).__name__} - {e}")
#                     import traceback
#                     print(f"[DEBUG] reply_stream 手动产出错误堆栈: {traceback.format_exc()}")
#                     break
#         except Exception as e:
#             print(f"[DEBUG] reply_stream __aiter__() 异常: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] reply_stream __aiter__() 错误堆栈: {traceback.format_exc()}")

#         print("🔄 DEBUG: 开始流式处理 reply_stream...")
#         await self.stream_message(reply_stream)

#     def build_runnable(self) -> Any:
#         print("🔨 DEBUG: build_runnable 开始执行")
        
#         # TODO: support model parameters. maybe we just add it to lm_provider_params in both 2.x and 3.x
#         print("🔧 DEBUG: 创建语言模型实例...")
#         try:
            
#             llm = self.config_manager.lm_provider(**self.config_manager.lm_provider_params)
#             #llm = self.config_manager.lm_provider(**params)
#             print(f"实际访问{self.config_manager.lm_provider_params}")
#             print(f"✅ DEBUG: 语言模型创建成功，类型: {type(llm)}")
#             print(f"🔧 DEBUG: LLM 实例: {repr(llm)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 语言模型创建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise
        
#         print("🔧 DEBUG: 构建基础链...")
#         try:
#             # 简化链构建，先测试基本功能
#             runnable = JUPYTERNAUT_PROMPT_TEMPLATE | llm | StrOutputParser()
#             print(f"✅ DEBUG: 基础链构建成功，类型: {type(runnable)}")
#             print(f"🔧 DEBUG: 基础链: {repr(runnable)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 基础链构建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("🔧 DEBUG: 添加消息历史支持...")
#         try:
#             runnable = RunnableWithMessageHistory(
#                 runnable=runnable,  #  type:ignore[arg-type]
#                 get_session_history=lambda: YChatHistory(ychat=self.ychat, k=2),
#                 input_messages_key="input",
#                 history_messages_key="history",
#             )
#             print(f"✅ DEBUG: 消息历史支持添加成功，类型: {type(runnable)}")
#             print(f"🔧 DEBUG: 最终 runnable: {repr(runnable)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 消息历史支持添加失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("✅ DEBUG: build_runnable 完成")
#         return runnable
from typing import Any, List, Iterator, Dict
from jupyterlab_chat.models import Message
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.base import RunnableLambda
from langchain_core.messages import BaseMessage
from ...history import YChatHistory
from ..base_persona import BasePersona, PersonaDefaults
from .prompt_template import JUPYTERNAUT_PROMPT_TEMPLATE, JupyternautVariables
import os
from ..company_ai.rag_system import RAGSystem
import requests
import json
import asyncio
from .env_config import get_model_config, get_embedding_config, validate_config

class CustomStrOutputParser(StrOutputParser):
    """自定义解析器，处理流式 chunk"""
    def parse(self, output):
        print(f"[DEBUG] CustomStrOutputParser 解析输出: {output}")
        if isinstance(output, dict) and "choices" in output:
            choices = output.get("choices", [])
            if choices and "delta" in choices[0]:
                content = choices[0]["delta"].get("content", "")
                print(f"[DEBUG] 提取 content: {content}")
                return content
            elif choices and "finish_reason" in choices[0]:
                print(f"[DEBUG] 结束原因: {choices[0]['finish_reason']}")
                return ""
        return str(output) if output else ""

class JupyternautPersona(BasePersona):
    print("🔧 DEBUG: JupyternautPersona 类被加载")

    def __init__(self, *args, **kwargs):
        print("🚀 DEBUG: JupyternautPersona.__init__ 被调用")
        super().__init__(*args, **kwargs)
        print("✅ DEBUG: JupyternautPersona.__init__ 完成")

    @property
    def defaults(self):
        return PersonaDefaults(
            name="Jupyternaut",
            avatar_path="/api/ai/static/jupyternaut.svg",
            description="The standard agent provided by JupyterLab. Currently has no tools.",
            system_prompt="...",
        )

    def _initialize_rag_system(self):
        print("🔧 DEBUG: _initialize_rag_system 开始执行")
        try:
            self._rag_system = RAGSystem()
            print("[DEBUG] RAGSystem 初始化成功")
        except Exception as e:
            print(f"[DEBUG] RAGSystem 初始化失败: {type(e).__name__} - {e}")
            import traceback
            print(f"[DEBUG] RAGSystem 错误堆栈: {traceback.format_exc()}")
            self._rag_system = None

    def get_rag_context(self, query: str) -> str:
        print(f"🔍 DEBUG: get_rag_context 查询: {query}")
        if not hasattr(self, '_rag_system') or self._rag_system is None:
            self._initialize_rag_system()
        if not self._rag_system:
            print("[DEBUG] RAGSystem 不可用")
            return f"RAG系统不可用，无法检索 '{query}' 的相关内容。"
        try:
            search_results = self._rag_system.search(query, top_k=3, max_content_length=500, max_segments=2)
            print(f"[DEBUG] RAG 检索结果数量: {len(search_results) if search_results else 0}")
            if not search_results:
                print(f"[DEBUG] 未找到 '{query}' 的相关文档")
                return f"未找到 '{query}' 的相关文档信息。"
            context_parts = ["## 相关文档信息\n"]
            for i, result in enumerate(search_results, 1):
                context_parts.append(f"### {i}. {result.get('title', '无标题')}")
                context_parts.append(f"**相似度**: {result.get('similarity_score', 0):.3f}")
                context_parts.append(f"**内容**:\n{result.get('content', '')}\n")
            context = "\n".join(context_parts)[:2000]
            print(f"[DEBUG] RAG 上下文长度: {len(context)} 字符")
            return context
        except Exception as e:
            print(f"[DEBUG] RAG 检索异常: {type(e).__name__} - {e}")
            import traceback
            print(f"[DEBUG] RAG 检索错误堆栈: {traceback.format_exc()}")
            return f"RAG检索异常: {e}"

    def check_context_length(self, formatted_prompt: str, history: List[BaseMessage], api_base: str, api_key: str, model: str = None) -> dict:
        print("[DEBUG] check_context_length 开始执行")
        
        # Use environment variable default if model not provided
        if model is None:
            model_config = get_model_config()
            model = model_config["model_id"]
        
        max_tokens = 128000
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            response = requests.get(f"{api_base}/models/{model}", headers=headers)
            if response.status_code == 200:
                model_info = response.json()
                max_tokens = model_info.get("max_tokens", 128000)
                print(f"[DEBUG] 从 API 获取模型 {model} 最大 token 数: {max_tokens}")
            else:
                print(f"[DEBUG] 获取模型信息失败，状态码: {response.status_code}，使用默认 128000")
        except Exception as e:
            print(f"[DEBUG] 获取模型信息异常: {type(e).__name__} - {e}")
            print("[DEBUG] 使用默认最大 token 数: 128000")

        def estimate_tokens(text: str) -> int:
            return len(text) // 2.5
        prompt_tokens = estimate_tokens(formatted_prompt)
        history_tokens = sum(estimate_tokens(str(msg)) for msg in history)
        total_tokens = prompt_tokens + history_tokens
        
        print(f"[DEBUG] 估算 token 数: prompt={prompt_tokens}, history={history_tokens}, total={total_tokens}")
        print(f"[DEBUG] 最大允许 token 数: {max_tokens}")
        
        return {
            "max_tokens": max_tokens,
            "prompt_tokens": prompt_tokens,
            "history_tokens": history_tokens,
            "total_tokens": total_tokens,
            "is_exceeded": total_tokens > max_tokens
        }

    async def process_message(self, message: Message) -> None:
        print("🚀 DEBUG: process_message 开始执行")
        print(f"🔍 DEBUG: 收到消息: {message.body}")
        
        self.send_message("🔧 调试：JupyternautPersona.process_message 正在执行...")
        
        if not self.config_manager.lm_provider:
            print("❌ DEBUG: 没有配置语言模型提供者")
            self.send_message(
                "No language model provider configured. Please set one in the Jupyter AI settings."
            )
            return

        provider_name = self.config_manager.lm_provider.name
        model_id = self.config_manager.lm_provider_params["model_id"]
        
        # Get API configuration from environment variables with fallback to config
        model_config = get_model_config()
        api_base = self.config_manager.lm_provider_params.get("openai_api_base", model_config["api_base"])
        
        # 优先使用环境变量中的API密钥，如果环境变量中有值的话
        env_api_key = model_config["api_key"]
        config_api_key = self.config_manager.lm_provider_params.get("openai_api_key", "")
        
        if env_api_key and env_api_key != "":
            api_key = env_api_key
            print(f"🔧 DEBUG: 使用环境变量中的API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        elif config_api_key and config_api_key != "":
            api_key = config_api_key
            print(f"🔧 DEBUG: 使用配置管理器中的API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        else:
            api_key = env_api_key  # 使用环境变量默认值
            print(f"🔧 DEBUG: 使用默认API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        
        print(f"🔧 DEBUG: 提供者: {provider_name}, 模型: {model_id}, API 端点: {api_base}")
        
        self.send_message(f"🔧 配置确认：提供者={provider_name}, 模型={model_id}")

        rag_context = self.get_rag_context(message.body)
        print(f"[DEBUG] RAG 上下文长度: {len(rag_context)} 字符")

        attach_context = self.process_attachments(message)
        print(f"📎 DEBUG: 附件上下文长度: {len(attach_context) if attach_context else 0}")

        context = rag_context + ("\n" + attach_context if attach_context else "")
        print(f"[DEBUG] 最终上下文长度: {len(context)} 字符")

        print("🔨 DEBUG: 开始构建 runnable...")
        try:
            runnable = self.build_runnable()
            print(f"✅ DEBUG: runnable 构建完成，类型: {type(runnable)}")
            self.send_message("🔧 runnable 构建成功")
        except Exception as e:
            print(f"❌ DEBUG: runnable 构建失败: {type(e).__name__} - {e}")
            import traceback
            print(f"❌ DEBUG: runnable 错误堆栈: {traceback.format_exc()}")
            self.send_message(f"❌ runnable 构建失败: {e}")
            return
        
        variables = JupyternautVariables(
            input=message.body,
            model_id=model_id,
            provider_name=provider_name,
            persona_name=self.name,
            context=context,
            history=[]  # 初始化为空
        )
        
        history = []
        try:
            session_history = YChatHistory(ychat=self.ychat, k=2).messages
            history = session_history if session_history else []
            print(f"[DEBUG] 历史消息数量: {len(history)}, 内容: {history}")
        except Exception as e:
            print(f"[DEBUG] 获取历史消息失败: {type(e).__name__} - {e}")

        variables_dict = variables.model_dump()
        variables_dict["history"] = history
        print(f"📝 DEBUG: 变量准备完成，input长度: {len(variables_dict.get('input', ''))}, context长度: {len(variables_dict.get('context', ''))}, history长度: {sum(len(str(msg)) for msg in history)}")

        print("🔍 DEBUG: 格式化 prompt...")
        try:
            formatted_prompt = JUPYTERNAUT_PROMPT_TEMPLATE.format(**variables_dict)
            print(f"[DEBUG] 格式化 prompt 长度: {len(formatted_prompt)} 字符")
        except Exception as e:
            print(f"[DEBUG] 格式化 prompt 失败: {type(e).__name__} - {e}")
            import traceback
            print(f"[DEBUG] 格式化 prompt 错误堆栈: {traceback.format_exc()}")
            self.send_message(f"❌ prompt 格式化失败: {e}")
            return

        print("🔍 DEBUG: 检查上下文长度...")
        length_info = self.check_context_length(formatted_prompt, history, api_base, api_key, model_id)
        print(f"[DEBUG] 上下文长度检查结果: {length_info}")
        if length_info["is_exceeded"]:
            self.send_message(f"❌ 上下文长度超过限制: 总计 {length_info['total_tokens']} tokens，最大允许 {length_info['max_tokens']} tokens")
            return

        # 使用 LangChain 流式输出（按句子缓冲）
        print("🔄 DEBUG: 开始创建 reply_stream...")
        try:
            reply_stream = runnable.astream(variables_dict)
            print(f"✅ DEBUG: reply_stream 创建成功，类型: {type(reply_stream)}")
            buffer = ""
            chunk_count = 0
            async for chunk in reply_stream:
                print(f"[DEBUG] LangChain chunk[{chunk_count}]: {chunk}")
                if chunk:
                    buffer += chunk
                    if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
                        self.send_message(buffer.strip())
                        print(f"[DEBUG] 发送句子: {buffer.strip()}")
                        buffer = ""
                    elif len(buffer) > 200:
                        self.send_message(buffer.strip())
                        print(f"[DEBUG] 发送长缓冲: {buffer.strip()}")
                        buffer = ""
                chunk_count += 1
            if buffer:
                self.send_message(buffer.strip())
                print(f"[DEBUG] 发送剩余缓冲: {buffer.strip()}")
            print(f"[DEBUG] LangChain 总计接收 {chunk_count} 个 chunk")
            if chunk_count == 0:
                self.send_message("❌ LangChain 未接收到任何 chunk，可能是解析问题")
        except Exception as e:
            print(f"[DEBUG] reply_stream 异常: {type(e).__name__} - {e}")
            import traceback
            print(f"[DEBUG] reply_stream 错误堆栈: {traceback.format_exc()}")
            self.send_message(f"❌ reply_stream 异常: {e}")

        # 调试：直接 API 调用（仅用于对比）
        print("🔍 DEBUG: 直接使用 API 流式输出（仅用于对比）...")
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = [
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": message.body}
            ]
            data = {
                "model": model_id,
                "messages": messages,
                "stream": True,
                "max_tokens": 4000,
                "temperature": 0.3
            }
            buffer = ""
            with requests.post(api_base, headers=headers, json=data, stream=True) as r:
                # 检查响应状态码
                if r.status_code != 200:
                    print(f"❌ 聊天API请求失败: {r.status_code} - {r.text}")
                    return
                
                chunk_count = 0
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        print(f"[DEBUG] API chunk[{chunk_count}]: {decoded_line}")
                        
                        # 检查是否包含错误信息
                        if "code" in decoded_line and "401" in decoded_line:
                            print(f"❌ 聊天API认证失败: {decoded_line}")
                            return
                        
                        if decoded_line.startswith("data: ") and decoded_line != "data: [DONE]":
                            try:
                                chunk_data = json.loads(decoded_line[6:])
                                if "choices" in chunk_data and chunk_data["choices"]:
                                    content = chunk_data["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        buffer += content
                                        if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
                                            print(f"[DEBUG] API 发送句子: {buffer.strip()}")
                                            buffer = ""
                                        elif len(buffer) > 200:
                                            print(f"[DEBUG] API 发送长缓冲: {buffer.strip()}")
                                            buffer = ""
                                chunk_count += 1
                            except json.JSONDecodeError:
                                print(f"[DEBUG] JSON 解析失败: {decoded_line}")
                if buffer:
                    print(f"[DEBUG] API 发送剩余缓冲: {buffer.strip()}")
                print(f"[DEBUG] API 总计接收 {chunk_count} 个 chunk")
        except Exception as e:
            print(f"[DEBUG] 直接 API 流式处理失败: {type(e).__name__} - {e}")
            import traceback
            print(f"[DEBUG] 错误堆栈: {traceback.format_exc()}")
            self.send_message(f"❌ API 流式处理失败: {e}")

    def build_runnable(self) -> Any:
        print("🔨 DEBUG: build_runnable 开始执行")
        
        print("🔧 DEBUG: 创建语言模型实例...")
        async def stream_llm(input: Any) -> Iterator[str]:
            print(f"[DEBUG] stream_llm 调用: input={str(input)[:50]}...")
            
            # Get API configuration from environment variables with fallback to config
            model_config = get_model_config()
            model_id = self.config_manager.lm_provider_params.get("model_id", model_config["model_id"])
            api_base = self.config_manager.lm_provider_params.get("openai_api_base", model_config["api_base"])
            
            # 优先使用环境变量中的API密钥，如果环境变量中有值的话
            env_api_key = model_config["api_key"]
            config_api_key = self.config_manager.lm_provider_params.get("openai_api_key", "")
            
            if env_api_key and env_api_key != "":
                api_key = env_api_key
                print(f"🔧 DEBUG: stream_llm 使用环境变量中的API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
            elif config_api_key and config_api_key != "":
                api_key = config_api_key
                print(f"🔧 DEBUG: stream_llm 使用配置管理器中的API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
            else:
                api_key = env_api_key  # 使用环境变量默认值
                print(f"🔧 DEBUG: stream_llm 使用默认API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
            prompt = str(input)  # 将输入转换为字符串
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    "max_tokens": 4000,
                    "temperature": 0.3
                }
                print(f"[DEBUG] 发送 API 请求到: {api_base}")
                print(f"[DEBUG] 请求头: {headers}")
                print(f"[DEBUG] 请求数据: {json.dumps(data, ensure_ascii=False)[:100]}...")
                with requests.post(
                    api_base,
                    headers=headers,
                    json=data,
                    stream=True
                ) as response:
                    # 检查响应状态码
                    if response.status_code != 200:
                        print(f"❌ 聊天API请求失败: {response.status_code} - {response.text}")
                        return
                    
                    chunk_count = 0
                    buffer = ""
                    in_code_block = False
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode("utf-8")
                            print(f"[DEBUG] Raw chunk[{chunk_count}]: {decoded_line}")
                            
                            # 检查是否包含错误信息
                            if "code" in decoded_line and "401" in decoded_line:
                                print(f"❌ 聊天API认证失败: {decoded_line}")
                                return
                            
                            if decoded_line.startswith("data: ") and decoded_line != "data: [DONE]":
                                try:
                                    chunk_data = json.loads(decoded_line[6:])
                                    print(f"[DEBUG] Parsed chunk[{chunk_count}]: {chunk_data}")
                                    if "choices" in chunk_data and chunk_data["choices"]:
                                        content = chunk_data["choices"][0].get("delta", {}).get("content", "")
                                        if content:
                                            buffer += content
                                            
                                            # 检查代码块开始
                                            if "```" in buffer and not in_code_block:
                                                parts = buffer.split("```", 1)
                                                if len(parts) == 2:
                                                    yield parts[0] + "```"
                                                    buffer = parts[1]
                                                    in_code_block = True
                                                else:
                                                    # 只有开始标记，继续缓冲
                                                    pass
                                            # 检查代码块结束
                                            elif "```" in buffer and in_code_block:
                                                parts = buffer.split("```", 1)
                                                if len(parts) == 2:
                                                    yield parts[0] + "```"
                                                    buffer = parts[1]
                                                    in_code_block = False
                                                else:
                                                    # 只有结束标记，继续缓冲
                                                    pass
                                            # 如果不在代码块中且没有特殊标记，直接输出
                                            elif not in_code_block and not "```" in buffer:
                                                yield content
                                                buffer = ""
                                        elif chunk_data["choices"][0].get("finish_reason"):
                                            yield ""
                                    else:
                                        print(f"[DEBUG] 跳过非生成 chunk: {chunk_data}")
                                    chunk_count += 1
                                except json.JSONDecodeError:
                                    print(f"[DEBUG] JSON 解析失败: {decoded_line}")
                    
                    # 处理剩余的缓冲内容
                    if buffer:
                        yield buffer
                    
                    print(f"[DEBUG] stream_llm 总计接收 {chunk_count} 个 chunk")
            except Exception as e:
                print(f"[DEBUG] stream_llm 异常: {type(e).__name__} - {e}")
                import traceback
                print(f"[DEBUG] 错误堆栈: {traceback.format_exc()}")
                raise

        try:
            llm = RunnableLambda(stream_llm)
            print(f"✅ DEBUG: 语言模型创建成功，类型: {type(llm)}")
        except Exception as e:
            print(f"❌ DEBUG: 语言模型创建失败: {type(e).__name__} - {e}")
            import traceback
            print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
            raise
        
        print("🔧 DEBUG: 构建基础链...")
        try:
            runnable = JUPYTERNAUT_PROMPT_TEMPLATE | llm | CustomStrOutputParser()
            print(f"✅ DEBUG: 基础链构建成功，类型: {type(runnable)}")
        except Exception as e:
            print(f"❌ DEBUG: 基础链构建失败: {type(e).__name__} - {e}")
            import traceback
            print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
            raise

        print("🔧 DEBUG: 添加消息历史支持...")
        try:
            history_obj = YChatHistory(ychat=self.ychat, k=2)
            try:
                history_messages = history_obj.messages
                print(f"[DEBUG] 历史消息: {history_messages}")
            except Exception as e:
                print(f"[DEBUG] 获取 YChatHistory 消息失败: {type(e).__name__} - {e}")
            
            runnable = RunnableWithMessageHistory(
                runnable=runnable,
                get_session_history=lambda: history_obj,
                input_messages_key="input",
                history_messages_key="history",
            )
            print(f"✅ DEBUG: 消息历史支持添加成功，类型: {type(runnable)}")
        except Exception as e:
            print(f"❌ DEBUG: 消息历史支持添加失败: {type(e).__name__} - {e}")
            import traceback
            print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
            raise

        print("✅ DEBUG: build_runnable 完成")
        return runnable
# from typing import Any, List, Iterator, Dict
# from jupyterlab_chat.models import Message
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.runnables.base import RunnableLambda
# from langchain_core.messages import BaseMessage
# from ...history import YChatHistory
# from ..base_persona import BasePersona, PersonaDefaults
# from .prompt_template import JUPYTERNAUT_PROMPT_TEMPLATE, JupyternautVariables
# import os
# import requests
# import json
# import asyncio
# import re
# from ..company_ai.rag_system import RAGSystem
# class CustomStrOutputParser(StrOutputParser):
#     """自定义解析器，处理流式 chunk"""
#     def parse(self, output):
#         print(f"[DEBUG] CustomStrOutputParser 解析输出: {output}")
#         if isinstance(output, dict) and "choices" in output:
#             choices = output.get("choices", [])
#             if choices and "delta" in choices[0]:
#                 content = choices[0]["delta"].get("content", "")
#                 print(f"[DEBUG] 提取 content: {content}")
#                 return content
#             elif choices and "finish_reason" in choices[0]:
#                 print(f"[DEBUG] 结束原因: {choices[0]['finish_reason']}")
#                 return ""
#         return str(output) if output else ""

# class JupyternautPersona(BasePersona):
#     print("🔧 DEBUG: JupyternautPersona 类被加载")

#     def __init__(self, *args, **kwargs):
#         print("🚀 DEBUG: JupyternautPersona.__init__ 被调用")
#         super().__init__(*args, **kwargs)
#         print("✅ DEBUG: JupyternautPersona.__init__ 完成")

#     @property
#     def defaults(self):
#         return PersonaDefaults(
#             name="Jupyternaut",
#             avatar_path="/api/ai/static/jupyternaut.svg",
#             description="The standard agent provided by JupyterLab. Currently has no tools.",
#             system_prompt="...",
#         )

#     def _initialize_rag_system(self):
#         print("🔧 DEBUG: _initialize_rag_system 开始执行")
#         try:
#             self._rag_system = RAGSystem()
#             print("[DEBUG] RAGSystem 初始化成功")
#         except Exception as e:
#             print(f"[DEBUG] RAGSystem 初始化失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] RAGSystem 错误堆栈: {traceback.format_exc()}")
#             self._rag_system = None

#     def get_rag_context(self, query: str) -> str:
#         print(f"🔍 DEBUG: get_rag_context 查询: {query}")
#         if not hasattr(self, '_rag_system') or self._rag_system is None:
#             self._initialize_rag_system()
#         if not self._rag_system:
#             print("[DEBUG] RAGSystem 不可用")
#             return f"RAG系统不可用，无法检索 '{query}' 的相关内容。"
#         try:
#             search_results = self._rag_system.search(query, top_k=3, max_content_length=500, max_segments=2)
#             print(f"[DEBUG] RAG 检索结果数量: {len(search_results) if search_results else 0}")
#             if not search_results:
#                 print(f"[DEBUG] 未找到 '{query}' 的相关文档")
#                 return f"未找到 '{query}' 的相关文档信息。"
#             context_parts = ["## 相关文档信息\n"]
#             for i, result in enumerate(search_results, 1):
#                 context_parts.append(f"### {i}. {result.get('title', '无标题')}")
#                 context_parts.append(f"**相似度**: {result.get('similarity_score', 0):.3f}")
#                 context_parts.append(f"**内容**:\n{result.get('content', '')}\n")
#             context = "\n".join(context_parts)[:2000]
#             print(f"[DEBUG] RAG 上下文长度: {len(context)} 字符")
#             return context
#         except Exception as e:
#             print(f"[DEBUG] RAG 检索异常: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] RAG 检索错误堆栈: {traceback.format_exc()}")
#             return f"RAG检索异常: {e}"

#     def check_context_length(self, formatted_prompt: str, history: List[BaseMessage], api_base: str, api_key: str, model: str = "gpt-4o") -> dict:
#         print("[DEBUG] check_context_length 开始执行")
        
#         max_tokens = 128000
#         try:
#             headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#             response = requests.get(f"{api_base}/models/{model}", headers=headers)
#             if response.status_code == 200:
#                 model_info = response.json()
#                 max_tokens = model_info.get("max_tokens", 128000)
#                 print(f"[DEBUG] 从 API 获取模型 {model} 最大 token 数: {max_tokens}")
#             else:
#                 print(f"[DEBUG] 获取模型信息失败，状态码: {response.status_code}，使用默认 128000")
#         except Exception as e:
#             print(f"[DEBUG] 获取模型信息异常: {type(e).__name__} - {e}")
#             print("[DEBUG] 使用默认最大 token 数: 128000")

#         def estimate_tokens(text: str) -> int:
#             return len(text) // 2.5
#         prompt_tokens = estimate_tokens(formatted_prompt)
#         history_tokens = sum(estimate_tokens(str(msg)) for msg in history)
#         total_tokens = prompt_tokens + history_tokens
        
#         print(f"[DEBUG] 估算 token 数: prompt={prompt_tokens}, history={history_tokens}, total={total_tokens}")
#         print(f"[DEBUG] 最大允许 token 数: {max_tokens}")
        
#         return {
#             "max_tokens": max_tokens,
#             "prompt_tokens": prompt_tokens,
#             "history_tokens": history_tokens,
#             "total_tokens": total_tokens,
#             "is_exceeded": total_tokens > max_tokens
#         }

#     def is_code_content(self, content: str) -> bool:
#         """Detect if content appears to be code (e.g., Python syntax)."""
#         code_patterns = [
#             r'^\s*def\s+\w+\s*\(',  # Function definition
#             r'^\s*import\s+\w+',     # Import statement
#             r'^\s*class\s+\w+',      # Class definition
#             r'^\s*[\w\s=]+:\s*$',    # Dictionary or type hints
#             r'^\s{2,}',              # Indented code
#             r'print\(',              # Common Python function
#         ]
#         return any(re.search(pattern, content, re.MULTILINE) for pattern in code_patterns)

#     def wrap_code_content(self, content: str, language: str = "python") -> str:
#         """Wrap content in Markdown code block markers if it's code."""
#         if self.is_code_content(content):
#             return f"```{language}\n{content.rstrip()}\n```"
#         return content

#     async def process_message(self, message: Message) -> None:
#         print("🚀 DEBUG: process_message 开始执行")
#         print(f"🔍 DEBUG: 收到消息: {message.body}")
        
#         self.send_message("🔧 调试：JupyternautPersona.process_message 正在执行...")
        
#         if not self.config_manager.lm_provider:
#             print("❌ DEBUG: 没有配置语言模型提供者")
#             self.send_message(
#                 "No language model provider configured. Please set one in the Jupyter AI settings."
#             )
#             return

#         provider_name = self.config_manager.lm_provider.name
#         model_id = self.config_manager.lm_provider_params["model_id"]
#         api_base = self.config_manager.lm_provider_params.get("openai_api_base", "http://ai.gffunds.com.cn/llmapi/v1")
#         api_key = self.config_manager.lm_provider_params.get("openai_api_key", "")
#         print(f"🔧 DEBUG: 提供者: {provider_name}, 模型: {model_id}, API 端点: {api_base}")
        
#         self.send_message(f"🔧 配置确认：提供者={provider_name}, 模型={model_id}")

#         rag_context = self.get_rag_context(message.body)
#         print(f"[DEBUG] RAG 上下文长度: {len(rag_context)} 字符")

#         attach_context = self.process_attachments(message)
#         print(f"📎 DEBUG: 附件上下文长度: {len(attach_context) if attach_context else 0}")

#         context = rag_context + ("\n" + attach_context if attach_context else "")
#         print(f"[DEBUG] 最终上下文长度: {len(context)} 字符")

#         print("🔨 DEBUG: 开始构建 runnable...")
#         try:
#             runnable = self.build_runnable()
#             print(f"✅ DEBUG: runnable 构建完成，类型: {type(runnable)}")
#             self.send_message("🔧 runnable 构建成功")
#         except Exception as e:
#             print(f"❌ DEBUG: runnable 构建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: runnable 错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ runnable 构建失败: {e}")
#             return
        
#         variables = JupyternautVariables(
#             input=message.body,
#             model_id=model_id,
#             provider_name=provider_name,
#             persona_name=self.name,
#             context=context,
#             history=[]  # 初始化为空
#         )
        
#         history = []
#         try:
#             session_history = YChatHistory(ychat=self.ychat, k=2).messages
#             history = session_history if session_history else []
#             print(f"[DEBUG] 历史消息数量: {len(history)}, 内容: {history}")
#         except Exception as e:
#             print(f"[DEBUG] 获取历史消息失败: {type(e).__name__} - {e}")

#         variables_dict = variables.model_dump()
#         variables_dict["history"] = history
#         print(f"📝 DEBUG: 变量准备完成，input长度: {len(variables_dict.get('input', ''))}, context长度: {len(variables_dict.get('context', ''))}, history长度: {sum(len(str(msg)) for msg in history)}")

#         print("🔍 DEBUG: 格式化 prompt...")
#         try:
#             formatted_prompt = JUPYTERNAUT_PROMPT_TEMPLATE.format(**variables_dict)
#             print(f"[DEBUG] 格式化 prompt 长度: {len(formatted_prompt)} 字符")
#         except Exception as e:
#             print(f"[DEBUG] 格式化 prompt 失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] 格式化 prompt 错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ prompt 格式化失败: {e}")
#             return

#         print("🔍 DEBUG: 检查上下文长度...")
#         length_info = self.check_context_length(formatted_prompt, history, api_base, api_key, model_id)
#         print(f"[DEBUG] 上下文长度检查结果: {length_info}")
#         if length_info["is_exceeded"]:
#             self.send_message(f"❌ 上下文长度超过限制: 总计 {length_info['total_tokens']} tokens，最大允许 {length_info['max_tokens']} tokens")
#             return

#         print("🔄 DEBUG: 开始创建 reply_stream...")
#         try:
#             reply_stream = runnable.astream(variables_dict)
#             print(f"✅ DEBUG: reply_stream 创建成功，类型: {type(reply_stream)}")
#             buffer = ""
#             code_block_buffer = ""
#             in_code_block = False
#             chunk_count = 0
#             async for chunk in reply_stream:
#                 print(f"[DEBUG] LangChain chunk[{chunk_count}]: {chunk}")
#                 if chunk:
#                     buffer += chunk
#                     if "```" in chunk:
#                         if in_code_block:
#                             code_block_buffer += chunk
#                             in_code_block = False
#                             formatted_content = self.wrap_code_content(code_block_buffer)
#                             self.send_message(formatted_content.strip())
#                             print(f"[DEBUG] 发送完整代码块: {formatted_content.strip()}")
#                             code_block_buffer = ""
#                         else:
#                             in_code_block = True
#                             pre_code = buffer[:buffer.rindex("```")].strip()
#                             if pre_code:
#                                 self.send_message(pre_code)
#                                 print(f"[DEBUG] 发送代码块前文本: {pre_code}")
#                             code_block_buffer = buffer[buffer.rindex("```"):]
#                             buffer = ""
#                     elif in_code_block:
#                         code_block_buffer += chunk
#                     else:
#                         if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
#                             formatted_content = self.wrap_code_content(buffer)
#                             self.send_message(formatted_content.strip())
#                             print(f"[DEBUG] 发送句子: {formatted_content.strip()}")
#                             buffer = ""
#                         elif len(buffer) > 200:
#                             formatted_content = self.wrap_code_content(buffer)
#                             self.send_message(formatted_content.strip())
#                             print(f"[DEBUG] 发送长缓冲: {formatted_content.strip()}")
#                             buffer = ""
#                 chunk_count += 1
#             if code_block_buffer:
#                 formatted_content = self.wrap_code_content(code_block_buffer)
#                 self.send_message(formatted_content.strip())
#                 print(f"[DEBUG] 发送剩余代码块: {formatted_content.strip()}")
#             elif buffer:
#                 formatted_content = self.wrap_code_content(buffer)
#                 self.send_message(formatted_content.strip())
#                 print(f"[DEBUG] 发送剩余缓冲: {formatted_content.strip()}")
#             print(f"[DEBUG] LangChain 总计接收 {chunk_count} 个 chunk")
#             if chunk_count == 0:
#                 self.send_message("❌ LangChain 未接收到任何 chunk，可能是解析问题")
#         except Exception as e:
#             print(f"[DEBUG] reply_stream 异常: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] reply_stream 错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ reply_stream 异常: {e}")

#         print("🔍 DEBUG: 直接使用 API 流式输出（仅用于对比）...")
#         try:
#             headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#             messages = [
#                 {"role": "system", "content": formatted_prompt},
#                 {"role": "user", "content": message.body}
#             ]
#             data = {
#                 "model": model_id,
#                 "messages": messages,
#                 "stream": True,
#                 "max_tokens": 4000,
#                 "temperature": 0.3
#             }
#             buffer = ""
#             code_block_buffer = ""
#             in_code_block = False
#             with requests.post(f"{api_base}/chat/completions", headers=headers, json=data, stream=True) as r:
#                 chunk_count = 0
#                 for line in r.iter_lines():
#                     if line:
#                         decoded_line = line.decode("utf-8")
#                         print(f"[DEBUG] API chunk[{chunk_count}]: {decoded_line}")
#                         if decoded_line.startswith("data: ") and decoded_line != "data: [DONE]":
#                             try:
#                                 chunk_data = json.loads(decoded_line[6:])
#                                 if "choices" in chunk_data and chunk_data["choices"]:
#                                     content = chunk_data["choices"][0].get("delta", {}).get("content", "")
#                                     if content:
#                                         buffer += content
#                                         if "```" in content:
#                                             if in_code_block:
#                                                 code_block_buffer += content
#                                                 in_code_block = False
#                                                 formatted_content = self.wrap_code_content(code_block_buffer)
#                                                 print(f"[DEBUG] API 发送完整代码块: {formatted_content.strip()}")
#                                                 code_block_buffer = ""
#                                             else:
#                                                 in_code_block = True
#                                                 pre_code = buffer[:buffer.rindex("```")].strip()
#                                                 if pre_code:
#                                                     formatted_content = self.wrap_code_content(pre_code)
#                                                     print(f"[DEBUG] API 发送代码块前文本: {formatted_content.strip()}")
#                                                 code_block_buffer = buffer[buffer.rindex("```"):]
#                                                 buffer = ""
#                                         elif in_code_block:
#                                             code_block_buffer += content
#                                         else:
#                                             if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
#                                                 formatted_content = self.wrap_code_content(buffer)
#                                                 print(f"[DEBUG] API 发送句子: {formatted_content.strip()}")
#                                                 buffer = ""
#                                             elif len(buffer) > 200:
#                                                 formatted_content = self.wrap_code_content(buffer)
#                                                 print(f"[DEBUG] API 发送长缓冲: {formatted_content.strip()}")
#                                                 buffer = ""
#                                 chunk_count += 1
#                             except json.JSONDecodeError:
#                                 print(f"[DEBUG] JSON 解析失败: {decoded_line}")
#                 if code_block_buffer:
#                     formatted_content = self.wrap_code_content(code_block_buffer)
#                     print(f"[DEBUG] API 发送剩余代码块: {formatted_content.strip()}")
#                 if buffer:
#                     formatted_content = self.wrap_code_content(buffer)
#                     print(f"[DEBUG] API 发送剩余缓冲: {formatted_content.strip()}")
#                 print(f"[DEBUG] API 总计接收 {chunk_count} 个 chunk")
#         except Exception as e:
#             print(f"[DEBUG] 直接 API 流式处理失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"[DEBUG] 错误堆栈: {traceback.format_exc()}")
#             self.send_message(f"❌ API 流式处理失败: {e}")

#     def build_runnable(self) -> Any:
#         print("🔨 DEBUG: build_runnable 开始执行")
        
#         print("🔧 DEBUG: 创建语言模型实例...")
#         async def stream_llm(input: Any) -> Iterator[str]:
#             print(f"[DEBUG] stream_llm 调用: input={str(input)[:50]}...")
#             model_id = self.config_manager.lm_provider_params.get("model_id", "gpt-4o")
#             api_base = self.config_manager.lm_provider_params.get("openai_api_base", "http://ai.gffunds.com.cn/llmapi/v1")
#             api_key = self.config_manager.lm_provider_params.get("openai_api_key", "")
#             prompt = str(input)
#             try:
#                 headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#                 data = {
#                     "model": model_id,
#                     "messages": [{"role": "user", "content": prompt}],
#                     "stream": True,
#                     "max_tokens": 4000,
#                     "temperature": 0.3
#                 }
#                 print(f"[DEBUG] 发送 API 请求: {json.dumps(data, ensure_ascii=False)[:100]}...")
#                 with requests.post(
#                     f"{api_base}/chat/completions",
#                     headers=headers,
#                     json=data,
#                     stream=True
#                 ) as response:
#                     chunk_count = 0
#                     buffer = ""
#                     code_block_buffer = ""
#                     in_code_block = False
#                     for line in response.iter_lines():
#                         if line:
#                             decoded_line = line.decode("utf-8")
#                             print(f"[DEBUG] Raw chunk[{chunk_count}]: {decoded_line}")
#                             if decoded_line.startswith("data: ") and decoded_line != "data: [DONE]":
#                                 try:
#                                     chunk_data = json.loads(decoded_line[6:])
#                                     print(f"[DEBUG] Parsed chunk[{chunk_count}]: {chunk_data}")
#                                     if "choices" in chunk_data and chunk_data["choices"]:
#                                         content = chunk_data["choices"][0].get("delta", {}).get("content", "")
#                                         if content:
#                                             buffer += content
#                                             if "```" in content:
#                                                 if in_code_block:
#                                                     code_block_buffer += content
#                                                     in_code_block = False
#                                                     formatted_content = self.wrap_code_content(code_block_buffer)
#                                                     yield formatted_content
#                                                     print(f"[DEBUG] 产出完整代码块: {formatted_content}")
#                                                     code_block_buffer = ""
#                                                 else:
#                                                     in_code_block = True
#                                                     pre_code = buffer[:buffer.rindex("```")].strip()
#                                                     if pre_code:
#                                                         formatted_content = self.wrap_code_content(pre_code)
#                                                         yield formatted_content
#                                                         print(f"[DEBUG] 产出代码块前文本: {formatted_content}")
#                                                     code_block_buffer = buffer[buffer.rindex("```"):]
#                                                     buffer = ""
#                                             elif in_code_block:
#                                                 code_block_buffer += content
#                                             else:
#                                                 if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
#                                                     formatted_content = self.wrap_code_content(buffer)
#                                                     yield formatted_content
#                                                     print(f"[DEBUG] 产出句子: {formatted_content}")
#                                                     buffer = ""
#                                                 elif len(buffer) > 200:
#                                                     formatted_content = self.wrap_code_content(buffer)
#                                                     yield formatted_content
#                                                     print(f"[DEBUG] 产出长缓冲: {formatted_content}")
#                                                     buffer = ""
#                                         elif chunk_data["choices"][0].get("finish_reason"):
#                                             yield ""
#                                     else:
#                                         print(f"[DEBUG] 跳过非生成 chunk: {chunk_data}")
#                                     chunk_count += 1
#                                 except json.JSONDecodeError:
#                                     print(f"[DEBUG] JSON 解析失败: {decoded_line}")
#                     if code_block_buffer:
#                         formatted_content = self.wrap_code_content(code_block_buffer)
#                         yield formatted_content
#                         print(f"[DEBUG] 产出剩余代码块: {formatted_content}")
#                     if buffer:
#                         formatted_content = self.wrap_code_content(buffer)
#                         yield formatted_content
#                         print(f"[DEBUG] 产出剩余缓冲: {formatted_content}")
#                     print(f"[DEBUG] stream_llm 总计接收 {chunk_count} 个 chunk")
#             except Exception as e:
#                 print(f"[DEBUG] stream_llm 异常: {type(e).__name__} - {e}")
#                 import traceback
#                 print(f"[DEBUG] 错误堆栈: {traceback.format_exc()}")
#                 raise

#         try:
#             llm = RunnableLambda(stream_llm)
#             print(f"✅ DEBUG: 语言模型创建成功，类型: {type(llm)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 语言模型创建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise
        
#         print("🔧 DEBUG: 构建基础链...")
#         try:
#             runnable = JUPYTERNAUT_PROMPT_TEMPLATE | llm | CustomStrOutputParser()
#             print(f"✅ DEBUG: 基础链构建成功，类型: {type(runnable)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 基础链构建失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("🔧 DEBUG: 添加消息历史支持...")
#         try:
#             history_obj = YChatHistory(ychat=self.ychat, k=2)
#             try:
#                 history_messages = history_obj.messages
#                 print(f"[DEBUG] 历史消息: {history_messages}")
#             except Exception as e:
#                 print(f"[DEBUG] 获取 YChatHistory 消息失败: {type(e).__name__} - {e}")
            
#             runnable = RunnableWithMessageHistory(
#                 runnable=runnable,
#                 get_session_history=lambda: history_obj,
#                 input_messages_key="input",
#                 history_messages_key="history",
#             )
#             print(f"✅ DEBUG: 消息历史支持添加成功，类型: {type(runnable)}")
#         except Exception as e:
#             print(f"❌ DEBUG: 消息历史支持添加失败: {type(e).__name__} - {e}")
#             import traceback
#             print(f"❌ DEBUG: 错误堆栈: {traceback.format_exc()}")
#             raise

#         print("✅ DEBUG: build_runnable 完成")
#         return runnable