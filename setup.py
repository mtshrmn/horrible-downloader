from setuptools import setup
from setuptools.command.install import install
import subprocess
import os

with open("README.md", 'r') as f:
    long_description = f.read()

class custom_install(install):
    def run(self):
        # check if webtorrent is installed
        if subprocess.call(["webtorrent", "-v"], shell=True):
            subprocess.call("npm install webtorrent-cli -g", shell=True)
        install.run(self)

setup(
    name='horrible-downloader',
    version='1.0.4',
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
        'python-levenshtein>=0.12',
    ],
    entry_points={
        "console_scripts": ["horrible-downloader=HorribleDownloader.cmd:cli"]
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    cmdclass={"install": custom_install}
)
