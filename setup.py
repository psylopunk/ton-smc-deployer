import setuptools
from glob import glob

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    install_requires = fh.read().split('\n')

setuptools.setup(
    name="xton",
    version="0.0.3",
    author="Maxim Gurov",
    author_email="psylopunk@protonmail.com",
    description="TON SMC deployer Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psylopunk/ton-smc-deployer",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apple Public Source License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    package_dir={
        "": "src",
    },
    package_data={
        'xton': ['*.func', '.fif']
    },
    install_requires=install_requires,
    packages=['xton'],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'xton = xton.main:main',
        ],
    }
)