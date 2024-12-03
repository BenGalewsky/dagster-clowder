from setuptools import find_packages, setup

setup(
    name="dagster_clowder",
    packages=find_packages(exclude=["dagster_clowder_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-postgres",
        "requests-toolbelt==1.0.0"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
