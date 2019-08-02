import os
from setuptools import setup
from setuptools.command.install import install
import subprocess

with open("README.md", 'r') as f:
    long_description = f.read()

class custom_install(install):
    def run(self):
        install.run(self)
        if os.name == "nt":
            #TODO: call post install for windows
            pass
        else:
            subprocess.call(["./post_install.sh"])

setup(
    name='Horrible-Downloader',
    version='0.1.6',
    packages=['HorribleDownloader'],
    url='https://github.com/Jelomite/horrible-downloader',
    license='MIT',
    author='Jelomite',
    author_email='moshesher1998@gmail.com',
    description='HorribleSubs API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'beautifulsoup4>=4',
        'requests>=2',
        'lxml>=4',
        'sty>=1.0.0b9',
        'fuzzywuzzy>=0.16',
        'python-levenshtein>=0.12'
    ],
    scripts=["bin/horrible-downloader.py"] if os.name == "nt" else ["bin/horrible-downloader"],
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    cmdclass={"install": custom_install}
)
