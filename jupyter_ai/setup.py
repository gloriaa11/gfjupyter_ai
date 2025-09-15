#!/usr/bin/env python3
"""
Setup script for jupyter-ai package
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Jupyter AI - AI-powered coding assistant for JupyterLab"

# Read version from _version.py
def get_version():
    version_path = os.path.join(os.path.dirname(__file__), '_version.py')
    with open(version_path, 'r', encoding='utf-8') as f:
        exec(open(version_path).read())
    return locals()['__version__']

setup(
    name="jupyter-ai-custom",
    version=get_version(),
    author="Your Company",
    author_email="your-email@company.com",
    description="Custom Jupyter AI with RAG system and company-specific features",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-company/jupyter-ai-custom",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jupyterlab>=4.0.0",
        "langchain>=0.1.0",
        "pydantic>=2.0.0",
        "requests>=2.25.0",
        "faiss-cpu>=1.7.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "tiktoken>=0.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "jupyter_ai": [
            "static/*",
            "personas/*/requirements.txt",
            "*.md",
        ],
    },
    entry_points={
        "jupyterlab.extension": [
            "jupyter-ai = jupyter_ai.extension",
        ],
    },
    zip_safe=False,
)