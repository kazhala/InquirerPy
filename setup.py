import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="InquirerPy",
    version="0.1.1",
    author="Kevin Zhuang",
    author_email="kevin7441@gmail.com",
    description="Enhaced Python port of Inquirer.js",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kazhala/InquirerPy",
    keywords="cli, prompt-toolkit, commandline, inquirer, development, command-line",
    packages=setuptools.find_packages(exclude=["tests*", "examples"]),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: Microsoft",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    install_requires=["prompt-toolkit>=3.0.1"],
)
