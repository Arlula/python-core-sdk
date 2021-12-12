import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='arlulacore',
    version='2.0.0',
    author="Arlula",
    author_email="tech@arlula.com",
    description="A package to facilitate access to the Arlula Imagery Marketplace API",

    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arlula/python-core-sdk.git",
    packages=["arlulacore"],
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
)
