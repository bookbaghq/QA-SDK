from setuptools import setup, find_packages

setup(
    name="bookbag",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    description="Bookbag Decision Gate SDK — real-time AI output evaluation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Bookbag",
    url="https://bookbag.ai",
)
