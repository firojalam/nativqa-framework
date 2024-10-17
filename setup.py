from setuptools import setup, find_packages

setup(
    name="nativqa",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here
    ],
    entry_points={
        'console_scripts': [
            'nativqa=nativqa.main:run_workflow',
        ],
    },
)
