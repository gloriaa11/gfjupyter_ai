import asyncio
from unittest.mock import AsyncMock, MagicMock
from jupyterlab_chat.models import Message
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# 假设这些是您提供的 JupyternautPersona 类的依赖
from jupyternaut import JupyternautPersona
from prompt_template import  JUPYTERNAUT_PROMPT_TEMPLATE, JupyternautVariables

async def test_jupyternaut_persona():
    print("🔧 开始测试 JupyternautPersona...")

    # 创建 mock 的 config_manager
    config_manager = MagicMock()
    config_manager.lm_provider = MagicMock(name="MockProvider")
    config_manager.lm_provider_params = {"model_id": "mock-model"}
    config_manager.lm_provider.name = "MockProvider"

    # 创建 mock 的语言模型
    mock_llm = AsyncMock()
    mock_llm.invoke = AsyncMock(return_value="This is a mock response from the language model.")
    mock_llm.astream = AsyncMock(return_value=AsyncMock(__aiter__=lambda: mock_stream()))

    # 模拟 RAGSystem
    mock_rag_system = MagicMock()
    mock_rag_system.search.return_value = [
        {"title": "Doc1", "content": "Jupyter AI is an AI-powered extension for JupyterLab.", "similarity_score": 0.95},
        {"title": "Doc2", "content": "It provides AI-driven features for coding.", "similarity_score": 0.90}
    ]

    # 模拟 YChatHistory
    mock_ychat_history = MagicMock()
    mock_ychat_history.get_messages.return_value = []

    # 模拟 stream_message 方法
    async def mock_stream_message(reply_stream):
        async for chunk in reply_stream:
            print(f"📤 收到流式输出: {chunk}")

    # 创建 JupyternautPersona 实例
    persona = JupyternautPersona()
    persona.config_manager = config_manager
    persona.ychat = MagicMock()
    persona._rag_system = mock_rag_system
    persona.send_message = MagicMock()
    persona.stream_message = mock_stream_message
    persona.process_attachments = MagicMock(return_value="")

    # 模拟语言模型提供者的实例化
    config_manager.lm_provider = MagicMock(return_value=mock_llm)

    # 测试消息
    test_message = Message(body="What is Jupyter AI?")

    print("🚀 测试 process_message 方法...")
    await persona.process_message(test_message)

    # 验证 send_message 被调用
    persona.send_message.assert_any_call("🔧 调试：JupyternautPersona.process_message 正在执行...")
    persona.send_message.assert_any_call("🔧 配置确认：提供者=MockProvider, 模型=mock-model")
    persona.send_message.assert_any_call("🔧 runnable 构建成功")
    print("✅ send_message 调用验证通过")

    print("✅ 测试完成！")

# 模拟流式输出的异步迭代器
async def mock_stream():
    yield "This is "
    yield "a mock "
    yield "response from "
    yield "the language model."

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_jupyternaut_persona())