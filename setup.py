from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prompt_compressor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A semantic text compression engine for LLM prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/prompt_compressor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "typer>=0.4.0",
        "pyyaml>=5.4.1",
    ],
    entry_points={
        "console_scripts": [
            "prompt-compress=prompt_compressor.cli:main",
        ],
    },
) 