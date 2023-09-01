from urllib.parse import urlparse

from setuptools import find_packages, setup

version = "0.1"


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

setup(
    name="opnsense-prom-exporter",
    version=version,
    description="OPNSense Prometheus exporter",
    author="Pierre Verkest",
    author_email="pierreverkest84@gmail.com",
    license="GNU GPL v3",
    namespace_packages=["opnsense_exporter"],
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    install_requires=requires,
    tests_require=requires + tests_requires,
    entry_points="""
        [console_scripts]
        opnsense-exporter=opnsense_exporter.server:run
        """,
)
