from setuptools import setup, find_packages

setup(
    name="pod5split",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "argparse",
        "pod5>=0.3.0",
        "pytest"
    ],
    entry_points={
        'console_scripts': [
            'pod5split=pod5split:main',
        ],
    },
    author="CRUK Cambridge Institute",
    description="This tool fills a hole in the ONT Pod5 tools suite to split a large Pod5 file into chunks of a given number of reads.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)

