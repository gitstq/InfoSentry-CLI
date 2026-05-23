#!/usr/bin/env python3
"""
Setup script for InfoSentry-CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name='infosentry-cli',
    version='1.0.0',
    description='Lightweight Open Source Intelligence Aggregation & Analysis Engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='gitstq',
    author_email='',
    url='https://github.com/gitstq/InfoSentry-CLI',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'infosentry=infosentry.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='osint intelligence security monitoring cli terminal dashboard',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/InfoSentry-CLI/issues',
        'Source': 'https://github.com/gitstq/InfoSentry-CLI',
    },
)
