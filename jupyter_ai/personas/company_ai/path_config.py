"""
路径配置工具，用于管理API知识库的绝对路径。
"""
import os
from pathlib import Path


def get_api_knowledge_base_path() -> Path:
    """
    获取API知识库的基础绝对路径。
    
    Returns:
        Path: API知识库的绝对路径
    """
    # 获取当前文件的目录
    current_dir = Path(__file__).parent
    
    # 构建到api_knowledge目录的绝对路径
    # 从 personas/company_ai/ 到 personas/api_knowledge/
    api_knowledge_path = current_dir.parent / "api_knowledge"
    
    return api_knowledge_path


def get_api_schemas_path() -> Path:
    """
    获取API schemas文件的绝对路径。
    
    Returns:
        Path: api_schemas.json的绝对路径
    """
    base_path = get_api_knowledge_base_path()
    return base_path / "api_schemas.json"


def get_extra_docs_path() -> Path:
    """
    获取额外文档目录的绝对路径。
    
    Returns:
        Path: extra文档目录的绝对路径
    """
    base_path = get_api_knowledge_base_path()
    return base_path / "extra"


def get_document_paths() -> list[Path]:
    """
    获取所有文档路径的列表。
    
    Returns:
        list[Path]: 文档路径列表
    """
    base_path = get_api_knowledge_base_path()
    
    # 获取所有.txt文件
    txt_files = list(base_path.glob("*.txt"))
    
    # 添加api_schemas.json
    api_schemas = base_path / "api_schemas.json"
    if api_schemas.exists():
        txt_files.append(api_schemas)
    
    return txt_files


def get_available_paths() -> dict[str, Path]:
    """
    获取所有可用的路径配置。
    
    Returns:
        dict[str, Path]: 路径配置字典
    """
    return {
        "api_knowledge_base": get_api_knowledge_base_path(),
        "api_schemas": get_api_schemas_path(),
        "extra_docs": get_extra_docs_path(),
        "document_paths": get_document_paths()
    }


def validate_paths() -> bool:
    """
    验证所有路径是否存在。
    
    Returns:
        bool: 如果所有路径都存在则返回True
    """
    paths = get_available_paths()
    
    for name, path in paths.items():
        if name == "document_paths":
            # 对于文档路径列表，检查是否有任何文件存在
            if not any(p.exists() for p in path):
                print(f"⚠️  警告: 没有找到任何文档文件在 {path[0].parent}")
                return False
        else:
            if not path.exists():
                print(f"⚠️  警告: 路径不存在: {name} = {path}")
                return False
        print(f"✅ 路径验证成功: {name} = {path}")
    
    return True