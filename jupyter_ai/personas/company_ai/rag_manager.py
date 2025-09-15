#!/usr/bin/env python3
"""
RAG系统管理脚本
用于初始化、测试和管理公司知识库
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from rag_system import RAGSystem
    print("✓ RAG系统模块导入成功")
except ImportError as e:
    print(f"✗ RAG系统模块导入失败: {e}")
    print("请确保已安装必要的依赖包")
    sys.exit(1)

def test_rag_system():
    """测试RAG系统"""
    print("\n=== 测试RAG系统 ===")
    
    try:
        # 初始化RAG系统
        print("正在初始化RAG系统...")
        rag = RAGSystem()
        print("✓ RAG系统初始化成功")
        
        # 获取知识库摘要
        print("\n获取知识库摘要...")
        summary = rag.get_knowledge_summary()
        print(summary)
        
        # 测试搜索功能
        print("\n=== 测试搜索功能 ===")
        test_queries = [
            "如何获取因子数据",
            "回测函数有哪些",
            "投资组合构建",
            "数据处理函数",
            "绩效分析"
        ]
        
        for query in test_queries:
            print(f"\n搜索查询: '{query}'")
            results = rag.search(query, top_k=3)
            
            if results:
                print(f"找到 {len(results)} 个相关结果:")
                for i, result in enumerate(results, 1):
                   # print(f"  {i}. {result['title']} (相似度: {result['similarity_score']:.3f})")
                    #print(f"     类型: {result.get('type', 'unknown')}")
                    if result.get('type') == 'api_function':
                        metadata = result.get('metadata', {})
                     #   print(f"     函数: {metadata.get('name', 'Unknown')}")
            else:
                print("  未找到相关结果")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG系统测试失败: {e}")
        return False

def update_knowledge_base():
    """更新知识库"""
    print("\n=== 更新知识库 ===")
    
    try:
        rag = RAGSystem()
        rag.update_knowledge_base()
        print("✓ 知识库更新成功")
        return True
    except Exception as e:
        print(f"✗ 知识库更新失败: {e}")
        return False

def show_knowledge_summary():
    """显示知识库摘要"""
    print("\n=== 知识库摘要 ===")
    
    try:
        rag = RAGSystem()
        summary = rag.get_knowledge_summary()
        print(summary)
        return True
    except Exception as e:
        print(f"✗ 获取知识库摘要失败: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    print("=== 检查依赖包 ===")
    
    required_packages = [
        'numpy',
        'sentence_transformers',
        'faiss-cpu'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'faiss-cpu':
                import faiss
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print(f"\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✓ 所有依赖包都已安装")
        return True

def main():
    """主函数"""
    print("公司知识库RAG系统管理工具")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python rag_manager.py test          # 测试RAG系统")
        print("  python rag_manager.py update        # 更新知识库")
        print("  python rag_manager.py summary       # 显示知识库摘要")
        print("  python rag_manager.py check         # 检查依赖包")
        print("  python rag_manager.py all           # 执行所有操作")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        check_dependencies()
    elif command == "test":
        if check_dependencies():
            test_rag_system()
    elif command == "update":
        if check_dependencies():
            update_knowledge_base()
    elif command == "summary":
        if check_dependencies():
            show_knowledge_summary()
    elif command == "all":
        if check_dependencies():
            print("\n" + "="*50)
            update_knowledge_base()
            print("\n" + "="*50)
            test_rag_system()
            print("\n" + "="*50)
            show_knowledge_summary()
    else:
        print(f"未知命令: {command}")
        print("可用命令: test, update, summary, check, all")

if __name__ == "__main__":
    main() 