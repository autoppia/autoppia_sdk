from setuptools import find_packages, setup

with open("exact_requirements.txt", "r") as f:  
    required = f.read().splitlines()

setup(
    name="autoppia_sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        req.strip() for req in required 
        if req.strip() and not req.startswith('#') and not req.startswith('-')
    ]
)
