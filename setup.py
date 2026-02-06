"""
Setup script for stacking-analysis package.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stacking-analysis",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Analysis tool for atomic stacking configurations in bilayer materials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anikeya9/stacking-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "stacking-analysis=stacking_cli:main",
        ],
    },
    keywords="materials-science stacking bilayer TMD computational-physics",
    project_urls={
        "Bug Reports": "https://github.com/anikeya9/stacking-analysis/issues",
        "Source": "https://github.com/anikeya9/stacking-analysis",
        "Documentation": "https://github.com/anikeya9/stacking-analysis/blob/main/README.md",
    },
)
