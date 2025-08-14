from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Get version from package
def get_version():
    with open("autoppia/__init__.py", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"

setup(
    name="autoppia-sdk",
    version=get_version(),
    author="Autoppia Team",
    author_email="support@autoppia.com",
    description="Comprehensive Python SDK for creating, deploying, and managing autonomous AI agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/autoppia/autoppia-sdk",
    project_urls={
        "Bug Reports": "https://github.com/autoppia/autoppia-sdk/issues",
        "Source": "https://github.com/autoppia/autoppia-sdk",
        "Documentation": "https://docs.autoppia.com",
        "Website": "https://autoppia.com",
    },
    packages=find_packages(exclude=["tests", "docs", "examples", "*.tests", "*.tests.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "full": [
            "langchain>=0.1.0",
            "langchain-openai>=0.1.0",
            "langchain-anthropic>=0.1.0",
            "websockets>=11.0.0",
            "httpx>=0.24.0",
            "selenium>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Text Processing :: Linguistic",
        "Framework :: AsyncIO",
        "Typing :: Typed",
    ],
    keywords=[
        "ai",
        "artificial-intelligence",
        "autonomous-agents",
        "llm",
        "language-models",
        "web-automation",
        "ai-workers",
        "machine-learning",
        "automation",
        "sdk",
        "api",
        "openai",
        "anthropic",
        "langchain",
    ],
    entry_points={
        "console_scripts": [
            "autoppia=autoppia.cli:main",
        ],
    },
    zip_safe=False,
    license="MIT",
    platforms=["any"],
    maintainer="Autoppia Team",
    maintainer_email="support@autoppia.com",
    download_url="https://github.com/autoppia/autoppia-sdk/releases",
    provides=["autoppia"],
    requires_python=">=3.8",
)
