import os
from setuptools import setup, find_packages

def read_version():
    with open("./wosit/version.txt", "r") as file:
        return file.read().strip()

# def read_requirements():
#     with open("requirements.txt") as f:
#         return [line.strip() for line in f if line.strip()]

package_list = find_packages()


setup(
    name="wosit",
    version=read_version(),
    author="Maxime Gras-Chevalier",
    author_email="",
    description="WoSIT is an automation tool made to replace make in many instances.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=package_list,
    package_data={
        'wosit': [
            'version.txt'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
    ],
    python_requires=">=3.6",
    install_requires=[], #read_requirements(),
    entry_points={
        "console_scripts": [
            "wosit=wosit.builder:main",
        ],
    },
)