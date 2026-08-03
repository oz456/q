from setuptools import setup, find_packages

setup(
    name="q-cli",
    version="0.1.0",
    description="A fast, streaming, multi-provider terminal AI chat client inspired by tgpt.",
    author="Student Developer",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "q=q.cli:main",
        ],
    },
    python_requires=">=3.8",
)
