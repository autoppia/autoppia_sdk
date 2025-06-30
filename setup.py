from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as f:
    required = f.read().splitlines()

setup(
    name="autoppia_sdk",
    version="0.1.0",
    author="Autoppia Team",
    author_email="support@autoppia.com",
    description="SDK for interacting with Autoppia platform and Automata client.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://autoppia.com",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    install_requires=required,
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
        ]
    },
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "isort",
            "build",
            "twine"
        ]
    },
    license="MIT",
)
