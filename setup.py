from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setup(
    name="autoppia",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        req.strip() for req in required
        if req.strip() and not req.startswith('#') and not req.startswith('-')
    ]
)
