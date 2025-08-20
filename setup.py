from setuptools import setup

setup(
    name="codehub",
    version="1.0",
    packages=["codehub"],
    python_requires="==3.9.*",
    install_requires=[
        "click>=8.0.0",
        "pyyaml==6.0.1",
        "google-cloud-container==2.0.1",
        "google-api-python-client==1.10.0",
        "kubernetes==11.0.0",
        "python-dotenv==0.13.0",
    ],
    entry_points="""
        [console_scripts]
        codehub=codehub.cli.entrypoint:cli
    """,
)
