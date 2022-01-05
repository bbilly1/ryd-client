"""setup file with project metadata"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ryd-client",
    version="0.0.3",
    author="Simon",
    author_email="simobilleter@gmail.com",
    description="api client for returnyoutubedislike.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bbilly1/ryd-client",
    project_urls={
        "Bug Tracker": "https://github.com/bbilly1/ryd-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"ryd_client": "ryd_client"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["requests"],
)
