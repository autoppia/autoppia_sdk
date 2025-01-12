from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setup(
    name="autoppia_sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=required
)
