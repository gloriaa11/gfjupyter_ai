import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import time
from ..jupyternaut.env_config import get_embedding_config, get_embedding_model_priority_list
from .path_config import get_api_knowledge_base_path, get_api_schemas_path, get_extra_docs_path, get_document_paths, validate_paths

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    print("警告: 缺少必要的依赖包。请安装: pip install sentence-transformers faiss-cpu numpy")

class DocumentChunker:
    """文档分块器，将长文档分割成适合向量化的片段"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, title: str = "") -> List[Dict[str, str]]:
        """将文本分割成块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 如果这不是最后一块，尝试在句号或换行处分割
            if end < len(text):
                # 寻找最近的句号或换行
                for i in range(end, max(start + self.chunk_size // 2, start), -1):
                    if text[i] in '.。\n':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    "title": title,
                    "start_pos": start,
                    "end_pos": end
                })
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks

class RAGSystem:
    """RAG系统：文档向量化、存储和检索"""
     
    def __init__(self, vector_db_path: str = None, index_path: str = None):
        """初始化RAG系统"""
        print("正在初始化RAG系统...")
        
        # 验证路径配置
        print("🔍 验证API知识库路径...")
        validate_paths()
        
        # 初始化组件
        self.embedding_model = None
        self.vector_db = None
        self.llm_client = None
        self.documents = []
        self.index = None
        
        # 设置知识库文件路径到api_knowledge目录
        api_knowledge_base = get_api_knowledge_base_path()
        if vector_db_path is None:
            self.vector_db_path = api_knowledge_base / "vector_db.pkl"
        else:
            self.vector_db_path = Path(vector_db_path)
            
        if index_path is None:
            self.index_path = api_knowledge_base / "faiss_index.bin"
        else:
            self.index_path = Path(index_path)
            
        self.document_hashes = None
        
        print(f"📁 知识库文件路径: {self.vector_db_path}")
        print(f"📁 索引文件路径: {self.index_path}")
        # 初始化嵌入模型
        if not self._initialize_embedding_model():
            raise RuntimeError("嵌入模型初始化失败")
        
        # 初始化LLM客户端
        if not self._initialize_llm_client():
            raise RuntimeError("LLM客户端初始化失败")
        
        # 加载或创建知识库
        self._load_or_create_knowledge_base()
        
        print("✓ RAG系统初始化成功")
    def _initialize_embedding_model(self):
        """初始化嵌入模型为远程API方式，按顺序尝试不同的模型"""
        # Get configuration from environment variables
        embedding_config = get_embedding_config()
        self.embedding_api_url = embedding_config["api_base"]
        self.embedding_api_key = embedding_config["api_key"]
        
        # Get model priority list from environment variables
        model_priority_list = get_embedding_model_priority_list()
        
        # 默认先尝试第一个模型
        self.embedding_model_name = model_priority_list[0]
        print(f"✅ 尝试初始化嵌入模型: {self.embedding_model_name}")
        
        # 这里可以添加模型可用性检测逻辑
        # 实际使用时，你可能需要发送测试请求来验证模型是否可用
        # 如果当前模型不可用，可以继续尝试列表中的下一个模型
        
        print(f"✅ 嵌入模型初始化为远程API: {self.embedding_api_url}, model={self.embedding_model_name}")
        return True
    
    def _load_or_create_knowledge_base(self):
        """加载或创建知识库"""
        if self.vector_db_path.exists() and self.index_path.exists():
            print("🔍 发现现有知识库，正在加载...")
            print(f"📁 知识库文件: {self.vector_db_path}")
            print(f"📁 索引文件: {self.index_path}")
            try:
                self._load_knowledge_base()
                print(f"✅ 知识库加载成功，包含 {len(self.documents)} 个文档")
                return
            except Exception as e:
                print(f"❌ 知识库加载失败: {e}")
                print("🔄 将重新创建知识库...")
        
        print("📚 没有找到现有知识库，将创建新的...")
        self.documents = self._load_documents()
        if self.documents:
            self._create_knowledge_base()
        else:
            print("没有找到可用的文档")
    def _load_knowledge_base(self):
        """加载现有知识库"""
        # 加载文档
        with open(self.vector_db_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.document_hashes = data.get('hashes', {})
            created_at = data.get('created_at', 0)
            model_name = data.get('model_name', 'unknown')
            
            print(f"📅 知识库创建时间: {time.ctime(created_at)}")
            print(f"🤖 使用模型: {model_name}")
        
        # 检查文件是否有变化
        # 跳过源文件变化检测，直接使用现有知识库
        print("✅ 直接使用现有知识库，跳过源文件变化检测")
        
        # 加载FAISS索引
        self.index = faiss.read_index(str(self.index_path))
        print(f"✅ 知识库加载完成，包含 {len(self.documents)} 个文档")
    
    def _check_files_changed(self):
        """检查源文件是否有变化"""
        if not self.document_hashes:
            return True
            
        for doc in self.documents:
            source = doc['source']
            if source in self.document_hashes:
                try:
                    if Path(source).exists():
                        current_hash = self._get_file_hash(Path(source))
                        if current_hash != self.document_hashes[source]:
                            print(f"🔄 文件已变化: {source}")
                            return True
                    else:
                        print(f"⚠️ 文件已删除: {source}")
                        return True
                except:
                    print(f"⚠️ 无法检查文件: {source}")
                    return True
        return False
    
    def _save_knowledge_base(self):
        """保存知识库"""
        # 计算文档哈希值
        if self.document_hashes is None:
            self.document_hashes = {}
            for doc in self.documents:
                source = doc['source']
                if source in self.document_hashes:
                    continue
                try:
                    if Path(source).exists():
                        self.document_hashes[source] = self._get_file_hash(Path(source))
                except:
                    self.document_hashes[source] = "unknown"
        
        # 保存文档和哈希值
        with open(self.vector_db_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'hashes': self.document_hashes,
                'created_at': time.time(),
                'model_name': self.embedding_model_name
            }, f)
        
        # 保存FAISS索引
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
    
    def _create_knowledge_base(self):
        """创建新的知识库"""
        print("正在创建新的知识库...")
        
        # 加载文档
        self._load_documents()
        
        # 向量化文档
        if self.documents:
            self._vectorize_documents()
            self._save_knowledge_base()
            print(f"知识库创建完成，包含 {len(self.documents)} 个文档片段")
        else:
            print("没有找到可用的文档")
    
    def _load_documents(self):
        """加载文档，限制数量避免内存溢出"""
        documents = []
        max_documents = 500  # 限制最大文档数量
        loaded_count = 0
        
        # 使用绝对路径获取文档路径
        document_paths = get_document_paths()
        
        for path in document_paths:
            if loaded_count >= max_documents:
                print(f"⚠️ 已达到最大文档数量限制 ({max_documents})，停止加载")
                break
                
            doc_path = Path(path)
            if doc_path.exists():
                print(f"📁 发现文档路径: {doc_path}")
                
                if doc_path.is_file():
                    # 单个文件
                    try:
                        if doc_path.suffix.lower() == '.json':
                            # JSON文件
                            with open(doc_path, 'r', encoding='utf-8') as f:
                                import json
                                data = json.load(f)
                                # 将JSON转换为文本
                                content = json.dumps(data, ensure_ascii=False, indent=2)
                                documents.append({
                                    'content': content,
                                    'source': str(doc_path)
                                })
                                loaded_count += 1
                                print(f"✅ 加载JSON文件: {doc_path.name} (总计: {loaded_count})")
                        else:
                            # 其他文本文件
                            with open(doc_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                documents.append({
                                    'content': content,
                                    'source': str(doc_path)
                                })
                                loaded_count += 1
                                print(f"✅ 加载文本文件: {doc_path.name} (总计: {loaded_count})")
                    except Exception as e:
                        print(f"❌ 加载文件失败 {doc_path}: {e}")
                        
                elif doc_path.is_dir():
                    # 目录
                    print(f"📂 扫描目录: {doc_path}")
                    for file_path in doc_path.rglob('*'):
                        if loaded_count >= max_documents:
                            print(f"⚠️ 已达到最大文档数量限制 ({max_documents})，停止扫描目录")
                            break
                            
                        if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.json', '.py', '.html']:
                            try:
                                if file_path.suffix.lower() == '.json':
                                    # JSON文件
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        import json
                                        data = json.load(f)
                                        content = json.dumps(data, ensure_ascii=False, indent=2)
                                        documents.append({
                                            'content': content,
                                            'source': str(file_path)
                                        })
                                        loaded_count += 1
                                        print(f"✅ 加载JSON文件: {file_path.name} (总计: {loaded_count})")
                                else:
                                    # 其他文本文件
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        documents.append({
                                            'content': content,
                                            'source': str(file_path)
                                        })
                                        loaded_count += 1
                                        print(f"✅ 加载文件: {file_path.name} (总计: {loaded_count})")
                            except Exception as e:
                                print(f"❌ 加载文件失败 {file_path}: {e}")
            else:
                print(f"⚠️ 文档路径不存在: {doc_path}")
        
        print(f"📚 总共加载了 {len(documents)} 个文档")
        # 修复：将文档赋值给self.documents
        self.documents = documents
        return documents
    
    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件的MD5哈希值"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _vectorize_documents(self):
        """向量化文档，分批处理避免内存溢出"""
        if not self.documents:
            return
        import requests
        
        texts = [doc["content"] for doc in self.documents]
        print(f"正在通过API生成文档向量, 总数: {len(texts)}")
        
        # 分批处理，每批最多50个文档
        batch_size = 50
        all_embeddings = []
        
        headers = {"Authorization": f"Bearer {self.embedding_api_key}", "Content-Type": "application/json"}
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            print(f"🔄 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_texts)} 个文档")
            
            payload = {
                "model": self.embedding_model_name,
                "input": batch_texts
            }
            
            try:
                print(f"🔍 DEBUG: 发送嵌入API请求到: {self.embedding_api_url}")
                print(f"🔍 DEBUG: 使用模型: {self.embedding_model_name}")
                print(f"🔍 DEBUG: 使用API密钥: {self.embedding_api_key[:8]}...{self.embedding_api_key[-4:] if len(self.embedding_api_key) > 12 else '***'}")
                
                resp = requests.post(self.embedding_api_url, headers=headers, json=payload, timeout=120)
                print(f"🔍 DEBUG: 嵌入API响应状态码: {resp.status_code}")
                print(f"🔍 DEBUG: 嵌入API响应内容长度: {len(resp.text)} 字符")
                
                if resp.status_code != 200:
                    print(f"❌ 嵌入API请求失败: {resp.status_code} - {resp.text[:200]}...")
                    raise Exception(f"嵌入API请求失败: {resp.status_code} - {resp.text[:200]}")
                    
                # 检查响应大小，避免内存溢出
                if len(resp.text) > 100 * 1024 * 1024:  # 100MB
                    print(f"⚠️ 响应过大 ({len(resp.text)} 字符)，跳过此批次")
                    continue
                
                data = resp.json()
                
                # 检查响应中是否包含错误信息
                if "code" in data and data["code"] != 200:
                    error_msg = data.get("msg", "未知错误")
                    print(f"❌ 嵌入API业务错误: {data['code']} - {error_msg}")
                    raise Exception(f"嵌入API业务错误: {data['code']} - {error_msg}")
                
                if not data or "data" not in data:
                    print(f"❌ 嵌入API响应格式错误: {data}")
                    raise Exception(f"嵌入API响应格式错误: {data}")
                    
                batch_embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(batch_embeddings)
                print(f"✅ 第 {batch_num} 批处理完成，获得 {len(batch_embeddings)} 个向量")
                
            except Exception as e:
                print(f"❌ 第 {batch_num} 批API嵌入获取失败: {e}")
                # 继续处理下一批，而不是完全失败
                continue
        
        if not all_embeddings:
            raise Exception("所有批次的嵌入获取都失败了")
            
        vectors = np.array(all_embeddings, dtype="float32")
        print(f"✅ 所有批次处理完成，总共获得 {len(all_embeddings)} 个向量，shape={vectors.shape}")
        # 创建FAISS索引
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        print(f"向量化完成，索引包含 {self.index.ntotal} 个向量")
        
        # 保存知识库到本地
        print("💾 保存知识库到本地...")
        self._save_knowledge_base()
        print(f"✅ 知识库已保存到: {self.vector_db_path}")
        print(f"✅ 索引已保存到: {self.index_path}")
    def _load_documents(self):
        """
        加载文档：
        1) 从 api_knowledge/api_schemas.json 读取由 .whl 提取的 API 模式（函数/类），一项一块；
        2) 扫描额外目录（.txt/.md/.json/.py/.html），分块后只挑选最可能有用的 Top-3 片段加入。
        """
        from pathlib import Path
        import json

        def _safe_json_load(path: Path):
            """容错读取 JSON：支持单个 JSON 数组、单个对象，或被多次 append 的“多段 JSON”"""
            text = path.read_text(encoding="utf-8")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                dec = json.JSONDecoder()
                idx, n = 0, len(text)
                all_items = []
                while idx < n:
                    while idx < n and text[idx].isspace():
                        idx += 1
                    if idx >= n:
                        break
                    try:
                        obj, end = dec.raw_decode(text, idx)
                        idx = end
                        if isinstance(obj, list):
                            all_items.extend(obj)
                        elif isinstance(obj, dict):
                            all_items.append(obj)
                        else:
                            all_items.append(obj)
                    except json.JSONDecodeError:
                        break
                return all_items

        def _infer_signature(name: str, params: dict, ret: dict) -> str:
            """从 parameters/return 粗略生成签名字符串"""
            props = (params or {}).get("properties", {}) or {}
            required = set((params or {}).get("required", []) or [])
            parts = []
            for pname, meta in props.items():
                if pname == "self":
                    continue
                ptype = str(meta.get("type", "any"))
                default = meta.get("default", None)
                if pname in required or default in (None, "None"):
                    parts.append(f"{pname}: {ptype}")
                else:
                    parts.append(f"{pname}: {ptype}={default}")
            rtype = (ret or {}).get("type", "any")
            return f"{name}({', '.join(parts)}) -> {rtype}"

        def _render_function_doc(name: str, desc: str, params: dict, ret: dict) -> str:
            """将函数信息渲染为统一文本"""
            sig = _infer_signature(name, params, ret)
            props = (params or {}).get("properties", {}) or {}
            required = set((params or {}).get("required", []) or [])
            lines = [
                f"[FUNCTION] {name}",
                "[DESCRIPTION]",
                (desc or "").strip() or "No description available.",
                "",
                "[SIGNATURE]",
                sig,
                "",
                "[PARAMETERS]",
            ]
            if props:
                for k, v in props.items():
                    if k == "self":
                        continue
                    t = str(v.get("type", "any"))
                    req = "required" if k in required else "optional"
                    default = v.get("default", None)
                    if default not in (None, "None"):
                        lines.append(f"- {k} ({t}, {req}, default={default})")
                    else:
                        lines.append(f"- {k} ({t}, {req})")
            else:
                lines.append("- (no parameters)")
            lines.extend(["", "[RETURN]"])
            lines.append(f"- type: {str((ret or {}).get('type', 'any'))}")
            return "\n".join(lines).strip()

        def _render_class_doc(cls_name: str, desc: str, methods: list, properties: list) -> str:
            """渲染类信息为可检索文本"""
            lines = [
                f"[CLASS] {cls_name}",
                "[DESCRIPTION]",
                (desc or "").strip() or "No description available.",
            ]
            if properties:
                lines.extend(["", "[PROPERTIES]"])
                for p in properties:
                    lines.append(f"- {p.get('name','unknown')}: {p.get('description','').strip() or 'No description'}")
            if methods:
                lines.extend(["", "[METHODS]"])
                for m in methods:
                    lines.append(f"- {m.get('name','unknown')}")
            return "\n".join(lines).strip()

        def _score_chunk(chunk: dict) -> float:
            """启发式为分块打分：偏向示例/代码/函数定义/用法等内容"""
            title = (chunk.get("title") or "").lower()
            text = (chunk.get("content") or "")
            text_l = text.lower()

            # 关键词与代码线索
            kw = [
                "example", "examples", "示例", "样例", "用法", "usage", "调用",
                "参数", "returns", "返回", "raise", "error", "异常",
                "def ", "class ", "```", "->", "return ", "import ", "from "
            ]
            score = 0.0
            for k in kw:
                score += text_l.count(k) * (2.0 if k.strip() in {"def", "class"} else 1.0)

            # 标题命中额外加分
            if any(k in title for k in ["example", "examples", "示例", "样例", "usage", "用法"]):
                score += 3.0

            # 代码风格字符比例（越“像代码”越高）
            code_signals = "(){}[]:;=.".join([""])  # 简单聚合
            code_hits = sum(text.count(s) for s in ["def ", "class ", "return", "(", ")", ":", "{", "}", "```"])
            score += 0.15 * code_hits

            # 长度惩罚/奖励：偏好 200~1200 字的中等片段
            L = len(text)
            if 200 <= L <= 1200:
                score += 1.5
            elif L > 3000:
                score -= 0.5  # 超长略降

            return score

        documents = []

        # 1) 读取 API 模式（由 .whl 提取生成）
        api_json_path = get_api_schemas_path()

        if api_json_path.exists():
            try:
                data = _safe_json_load(api_json_path)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    for key in ("functions", "classes", "apis", "items"):
                        v = data.get(key)
                        if isinstance(v, list):
                            items.extend(v)
                    if not items:
                        items = [data]
                else:
                    items = [data]

                for it in items:
                    it_type = (it or {}).get("type", "").lower()
                    if it_type == "function":
                        name = it.get("name", "unknown")
                        desc = it.get("description", "")
                        params = it.get("parameters", {})
                        ret = it.get("return") or it.get("returns") or {}
                        content = _render_function_doc(name, desc, params, ret)
                        documents.append({
                            "id": f"api::{name}",
                            "title": name,
                            "type": "api_function",
                            "priority": 1.0,
                            "source": str(api_json_path),
                            "content": content
                        })

                    elif it_type == "class":
                        cls_name = it.get("name", "UnknownClass")
                        desc = it.get("description", "")
                        methods = it.get("methods", []) or []
                        properties = it.get("properties", []) or []

                        class_content = _render_class_doc(cls_name, desc, methods, properties)
                        documents.append({
                            "id": f"api_class::{cls_name}",
                            "title": cls_name,
                            "type": "api_class",
                            "priority": 0.9,
                            "source": str(api_json_path),
                            "content": class_content
                        })

                        for m in methods:
                            if not isinstance(m, dict):
                                continue
                            if m.get("name", "").startswith("_"):
                                continue
                            m_name = f"{cls_name}.{m.get('name','unknown')}"
                            m_desc = m.get("description", "")
                            m_params = m.get("parameters", {})
                            m_ret = m.get("return") or m.get("returns") or {}
                            m_content = _render_function_doc(m_name, m_desc, m_params, m_ret)
                            documents.append({
                                "id": f"api::{m_name}",
                                "title": m_name,
                                "type": "api_function",
                                "priority": 1.0,
                                "source": str(api_json_path),
                                "content": m_content
                            })
                    else:
                        documents.append({
                            "id": f"api_misc::{it.get('name','unknown')}",
                            "title": it.get("name", "unknown"),
                            "type": "api_misc",
                            "priority": 0.8,
                            "source": str(api_json_path),
                            "content": json.dumps(it, ensure_ascii=False, indent=2)
                        })
            except Exception as e:
                print(f"❌ 加载API知识文件失败: {e}")
        else:
            print("⚠️ 未找到 api_schemas.json")

        # 2) 其它文档选择性分块（Top-3 片段挑选）
        extra_dir = get_extra_docs_path()

        if extra_dir.exists() and extra_dir.is_dir():
            for file_path in extra_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.json', '.py', '.html']:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
                        chunks = chunker.chunk_text(content, title=file_path.name)

                        # 仅选择最可能有用的 Top-3 片段
                        scored = sorted(chunks, key=_score_chunk, reverse=True)
                        topk = scored[:min(3, len(scored))]

                        for idx, chunk in enumerate(topk):
                            documents.append({
                                "id": f"{file_path.name}::top{idx}",
                                "content": chunk['content'],
                                "title": chunk.get('title', file_path.name),
                                "type": "document",
                                "priority": 0.6,
                                "source": str(file_path)
                            })
                    except Exception as e:
                        print(f"❌ 加载文件失败 {file_path}: {e}")

        self.documents = documents
        return documents

    def update_knowledge_base(self):
        """更新知识库"""
        print("正在更新知识库...")
        
        # 重新加载文档
        self._load_documents()
        
        # 重新向量化
        if self.documents:
            self._vectorize_documents()
            self._save_knowledge_base()
            print(f"知识库更新完成，包含 {len(self.documents)} 个文档片段")
        else:
            print("没有找到可用的文档")
    
    def get_knowledge_summary(self) -> str:
        """获取知识库摘要"""
        if not self.documents:
            return "知识库为空"
        
        # 统计信息
        total_chunks = len(self.documents)
        api_functions = len([d for d in self.documents if d.get("type") == "api_function"])
        api_classes = len([d for d in self.documents if d.get("type") == "api_class"])
        documents = len([d for d in self.documents if d.get("type") == "document"])
        
        summary = f"## 知识库摘要\n\n"
        summary += f"- 总文档片段数: {total_chunks}\n"
        summary += f"- API函数: {api_functions}\n"
        summary += f"- API类: {api_classes}\n"
        summary += f"- 文档片段: {documents}\n\n"
        
        # 显示一些示例
        summary += "### 示例API函数\n"
        api_examples = [d for d in self.documents if d.get("type") == "api_function"][:5]
        for doc in api_examples:
            summary += f"- {doc['title']}: {doc['content'][:100]}...\n"
        
        summary += "\n### 示例文档\n"
        doc_examples = [d for d in self.documents if d.get("type") == "document"][:3]
        for doc in doc_examples:
            summary += f"- {doc['title']}: {doc['content'][:100]}...\n"
        
        return summary 
    def _initialize_llm_client(self):
        """初始化LLM客户端"""
        try:
            import sys
            import os
            
            # 使用硬编码路径
            project_root = r"C:\Users\dc-develop-2\Desktop\work\pre\code\jupyter-ai\jupyter-ai"
            sys.path.insert(0, project_root)
            
            from llm_client import LLMClient
            from api_config import API_KEY
            
            self.llm_client = LLMClient(api_key=API_KEY)
            print("✅ LLM客户端初始化成功")
            return True
        except Exception as e:
            print(f"❌ LLM客户端初始化失败: {e}")
            return False
    def search(self, query: str, top_k: int = 3, max_content_length: int = 500, max_segments: int = 2):
        """
        基于 TF-IDF 的轻量相似度检索：
        - 对每个文档按段落/代码块分段，计算段落与查询的相似度
        - 每个文档仅选出相似度最高的 max_segments 个片段，按 max_content_length 拼接
        - 文档得分 = 选中片段相似度的平均值 * 类型/优先级加权
        - 返回按得分排序的 top_k 文档（每条包含压缩后的 content 与 similarity_score）
        """
        import re, math, copy

        if not getattr(self, "documents", None):
            if hasattr(self, "_load_documents"):
                print("[DEBUG] 文档未加载，调用 _load_documents()")
                self._load_documents()
            else:
                raise AttributeError("RAGSystem 缺少 documents，请先实现并调用 _load_documents()")

        # ---------- 基础工具 ----------
        def normalize_text(t: str) -> str:
            return (t or "").strip()

        def tokenize(t: str):
            """支持英文单词、数字、以及逐字的中日韩统一表意文字"""
            t = t.lower()
            words = re.findall(r"[a-z_][a-z0-9_]+", t)
            nums  = re.findall(r"\d+(?:\.\d+)?", t)
            cjk   = re.findall(r"[\u4e00-\u9fff]", t)
            return words + nums + cjk

        def split_segments(text: str):
            """
            将文档切成语义段：
            - 先按三引号/代码围栏/空行切
            - 再对超长段按 ~400 字做二次切分
            """
            text = normalize_text(text)
            if not text:
                return []

            # 代码围栏优先
            fence_split = re.split(r"(```.*?```)", text, flags=re.S)
            raw_segs = []
            for part in fence_split:
                if not part.strip():
                    continue
                if part.startswith("```") and part.endswith("```"):
                    raw_segs.append(part)
                else:
                    raw_segs.extend([s for s in re.split(r"\n\s*\n", part) if s.strip()])

            # 二次长度切分（~400 字）
            final = []
            for seg in raw_segs:
                s = seg.strip()
                if len(s) <= 600:
                    final.append(s)
                    continue
                # 按句号/换行做软切，再兜底硬切
                pieces = re.split(r"(?<=[。！？.!?])\s+|\n{1,}", s)
                buf = ""
                for p in pieces:
                    if not p.strip():
                        continue
                    if len(buf) + len(p) + 1 <= 600:
                        buf = (buf + "\n" + p) if buf else p
                    else:
                        if buf:
                            final.append(buf)
                        buf = p
                if buf:
                    final.append(buf)

                # 兜底硬切，防止极端长段
                hard_final = []
                for s2 in final[-3:]:  # 仅对刚加入的段兜底
                    if len(s2) <= 800:
                        hard_final.append(s2)
                    else:
                        for i in range(0, len(s2), 700):
                            hard_final.append(s2[i:i+700])
                final = final[:-3] + hard_final if len(final) >= 3 else hard_final
            return final

        # ---------- 构建分段语料与 DF ----------
        corpus_segments = []  # [(doc_idx, seg_idx, seg_text, type, priority)]
        for i, d in enumerate(self.documents):
            content = normalize_text(d.get("content", ""))
            if not content:
                continue
            segs = split_segments(content)
            typ = d.get("type", "document")
            pri = float(d.get("priority", 1.0))
            for j, s in enumerate(segs):
                corpus_segments.append((i, j, s, typ, pri))

        if not corpus_segments:
            print("[DEBUG] 没有可检索的分段语料")
            return []

        # 计算 DF
        df = {}
        for _, _, seg_text, _, _ in corpus_segments:
            toks = set(tokenize(seg_text))
            for t in toks:
                df[t] = df.get(t, 0) + 1
        N = len(corpus_segments)
        idf = {t: math.log(1.0 + N / (dfc + 1.0)) for t, dfc in df.items()}

        # 查询向量
        q_tokens = tokenize(query or "")
        if not q_tokens:
            print("[DEBUG] 查询为空或未能产生有效 token")
            return []

        def tfidf_vec(tokens):
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0.0) + 1.0
            # 归一化
            length = sum(v * v for v in tf.values()) ** 0.5 or 1.0
            # 乘以 idf
            vec = {t: (tf[t] / length) * idf.get(t, math.log(1.0 + N)) for t in tf}
            return vec

        q_vec = tfidf_vec(q_tokens)

        def cos_sim(vec_a, vec_b):
            # 稀疏向量点积
            if len(vec_a) > len(vec_b):
                vec_a, vec_b = vec_b, vec_a
            s = 0.0
            for k, va in vec_a.items():
                vb = vec_b.get(k)
                if vb:
                    s += va * vb
            # 归一（vec_b 已在 tfidf_vec 里做了 L2 近似）
            return s

        # 预计算每个分段向量
        seg_vecs = []
        for tup in corpus_segments:
            seg_vecs.append(tfidf_vec(tokenize(tup[2])))

        # ---------- 每文档挑选 top 段落 ----------
        # 类型加权
        type_weight = {
            "api_function": 1.3,
            "api_class":    1.15,
            "code_block":   1.05,
            "example_snippet": 1.05,
            "document":     1.0,
            "api_misc":     0.95
        }

        from collections import defaultdict
        per_doc_candidates = defaultdict(list)  # doc_idx -> [(seg_text, sim, typ, pri)]

        for (i, j, seg_text, typ, pri), seg_vec in zip(corpus_segments, seg_vecs):
            base_sim = cos_sim(q_vec, seg_vec)
            boost = type_weight.get(typ, 1.0) * float(pri or 1.0)
            sim = base_sim * boost
            per_doc_candidates[i].append((seg_text, sim, typ, pri))

        # 为每个文档选出相似度最高的 max_segments 个片段，并按长度预算拼接
        scored_docs = []
        for doc_idx, cand in per_doc_candidates.items():
            if not cand:
                continue
            cand.sort(key=lambda x: x[1], reverse=True)
            chosen = cand[:max_segments]

            selected_content = []
            total_len = 0
            for seg_text, seg_sim, _typ, _pri in chosen:
                seg_text = seg_text.strip()
                if not seg_text:
                    continue
                if total_len + len(seg_text) <= max_content_length:
                    selected_content.append(seg_text)
                    total_len += len(seg_text)
                else:
                    remaining = max_content_length - total_len
                    if remaining > 50:  # 避免过短碎片
                        selected_content.append(seg_text[:remaining] + " …")
                        total_len += remaining
                    break

            if not selected_content:
                # 回退：直接截取原文前 max_content_length
                raw = normalize_text(self.documents[doc_idx].get("content", ""))[:max_content_length]
                if raw:
                    selected_content = [raw + (" …" if len(raw) == max_content_length else "")]
                else:
                    continue

            # 文档得分：已选片段相似度的均值（或最大值也可）
            doc_score = sum(s for _, s, _, _ in chosen) / max(1, len(chosen))

            # 组装结果条目（不破坏原 self.documents）
            d = self.documents[doc_idx]
            new_doc = {
                "id": d.get("id"),
                "title": d.get("title"),
                "type": d.get("type"),
                "priority": d.get("priority", 1.0),
                "source": d.get("source"),
                "content": "\n\n".join(selected_content),
                "similarity_score": float(doc_score),
            }
            scored_docs.append(new_doc)

        # ---------- 全局排序并裁剪 ----------
        scored_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = scored_docs[:max(1, top_k)]

        # 调试输出
        print(f"[DEBUG] RAGSystem.search 完成，返回 {len(results)} 个结果")
        for idx, r in enumerate(results):
            clen = len(r.get("content") or "")
            print(f"[DEBUG] Top{idx+1} 标题: {r.get('title')} | 类型: {r.get('type')} | 分数: {r['similarity_score']:.4f} | 长度: {clen}")

        return results
