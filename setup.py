import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="filecollector",
    version="0.0.1",
    author="Oliver Szabo",
    author_email="oleewere@gmail.com",
    description="Simple file collector - compress/serve/send/anonymizie files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oleewere/filecollector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)