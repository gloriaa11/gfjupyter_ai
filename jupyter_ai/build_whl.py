#!/usr/bin/env python3
"""
构建whl文件的脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', 'jupyter_ai_custom.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def main():
    print("🚀 开始构建 Jupyter AI Custom whl 文件")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 安装构建依赖
    if not run_command("pip install build wheel setuptools", "安装构建依赖"):
        sys.exit(1)
    
    # 构建whl文件
    if not run_command("python -m build", "构建whl文件"):
        sys.exit(1)
    
    # 检查构建结果
    dist_dir = Path("dist")
    if dist_dir.exists():
        whl_files = list(dist_dir.glob("*.whl"))
        if whl_files:
            print(f"\n✅ 构建成功！")
            print(f"📦 whl文件位置:")
            for whl_file in whl_files:
                file_size = whl_file.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {whl_file} ({file_size:.2f} MB)")
            
            print(f"\n📋 安装命令:")
            print(f"   pip install {whl_files[0]}")
            
            print(f"\n📋 分发说明:")
            print(f"   1. 将whl文件分发给其他用户")
            print(f"   2. 用户运行: pip install {whl_files[0]}")
            print(f"   3. 配置环境变量（参考README.md）")
            print(f"   4. 重启JupyterLab")
        else:
            print("❌ 未找到whl文件")
            sys.exit(1)
    else:
        print("❌ dist目录不存在")
        sys.exit(1)

if __name__ == "__main__":
    main()