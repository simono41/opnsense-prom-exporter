import pathlib
from urllib.parse import urlparse

from setuptools import find_packages, setup

version = "0.4.0"
HERE = pathlib.Path(__file__).parent


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f.read().splitlines():
            if req.strip().startswith("git"):
                req = urlparse(req.strip()).fragment.split("=")[1]
            if req.strip().startswith("-e"):
                req = urlparse(req.strip().split()[1]).fragment.split("=")[1]
            if not req.strip().startswith("#") and not req.strip().startswith("--"):
                required.append(req)
    return required


requires = parse_requirements("requirements.txt")
tests_requires = parse_requirements("requirements.tests.txt")
README = (HERE / "README.md").read_text()

setup(
    name="opnsense-prom-exporter",
    version=version,
    description="OPNSense Prometheus exporter",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Pierre Verkest",
    author_email="pierreverkest84@gmail.com",
    url="https://gitlab.com/micro-entreprise/opnsense-prom-exporter",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    namespace_packages=["opnsense_exporter"],
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    install_requires=requires,
    tests_require=requires + tests_requires,
    entry_points="""
        [console_scripts]
        opnsense-exporter=opnsense_exporter.server:run
        """,
)
