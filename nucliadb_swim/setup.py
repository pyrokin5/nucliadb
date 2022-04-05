import re

from setuptools import find_packages, setup  # type: ignore

with open("README.md") as f:
    readme = f.read()

with open("LICENSE-MIT") as f:
    license = f.read()


def load_reqs(filename):
    with open(filename) as reqs_file:
        return [
            line
            for line in reqs_file.readlines()
            if not (
                re.match(r"\s*#", line)  # noqa
                or re.match("-e", line)
                or re.match("-r", line)
            )
        ]


requirements = load_reqs("requirements.txt")

setup(
    name="nucliadb_swim",
    version="0.3.8",
    author="nucliadb Authors",
    author_email="nucliadb@nuclia.com",
    description="SWIM protocol implementation for exchanging cluster "
    "membership status and metadata.",
    long_description=readme + license,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/nuclia/nucliadb",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    packages=find_packages(),
    install_requires=requirements,
)
