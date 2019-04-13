import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pandas==0.23.4',
    'requests==2.19.1',
    'bs4==0.0.1',
]

test_requirements = [
    'pytest==4.0.1'
]


about = {}
with open(os.path.join(here, 'edgar', '__version__.py'), mode='r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.md', mode='r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    packages=['edgar'],
    keywords=['sec', 'edgar', 'financials', 'stock', 'fundamental', 'analysis'],
    python_requires="==3.7",
    install_requires=requires,
    tests_require=test_requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)