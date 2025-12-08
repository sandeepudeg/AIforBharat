from setuptools import setup, find_packages

setup(
    name="bedrock-rag-retrieval",
    version="0.1.0",
    description="Bedrock RAG Retrieval System for document ingestion and semantic search",
    author="Development Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "boto3>=1.26.0",
        "opensearch-py>=2.0.0",
        "hypothesis>=6.70.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "hypothesis>=6.70.0",
        ],
    },
)
