from setuptools import setup, find_packages
from pathlib import Path

# Get the directory where this file lives
here = Path(__file__).parent

# Read dependencies from requirements.txt
requirements = (here / "requirements.txt").read_text(encoding="utf-8").splitlines()

# Read long description from README.md
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="autoppia",
    version="0.1.0",
    author="Autoppia Team",
    author_email="team@autoppia.com",
    description="SDK and tools for interacting with the Autoppia platform and Automata agents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://autoppia.com",
    packages=find_packages(),  # Make sure __init__.py files exist!
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
