from setuptools import setup, find_packages

setup(
    name="nativqa",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here
        "google-search-results==2.4.2",
        "python-dotenv==1.0.1",
        "tqdm==4.66.6"
    ]
)
