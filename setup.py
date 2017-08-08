try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import parrot38

setup(
    name="parrot38",
    version=parrot38.__version__,
    description="Write a blog in plain text with multiple entries per file",
    url="https://github.com/sio/parrot38",
    author=parrot38.__author__,
    author_email="sio.wtf@gmail.com",
    license="Apache License 2.0",
    platforms="any",
    py_modules=["parrot38"],
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.3",
    )
