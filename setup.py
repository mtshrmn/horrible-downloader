from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='Horrible-Downloader',
    version='0.0.3',
    packages=['HorribleDownloader'],
    url='https://github.com/Jelomite/horrible-downloader',
    license='MIT',
    author='Jelomite',
    author_email='moshesher1998@gmail.com',
    description='HorribleSubs API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)