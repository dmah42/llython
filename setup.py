import os
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="llython",
    version="0.0.1",
    author="Dominic Hamon",
    author_email="dom.hamon@gmail.com",
    url="https://github.com/dominichamon/llython",
    description="Compile python through LLVM",
    install_requires=['llvmlite'],
    license = "Apache 2.0",
    keywords = "llvm",
    long_description=read('README.md'),
    packages=['llython'],
    classifiers = [
      "Development Status :: 2 - Pre-Alpha",
      "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
      'console_scripts': [
        'llython = llython.__main__:main'
      ]
    },
)
