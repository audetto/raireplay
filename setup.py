from os.path import dirname, join
from setuptools import setup, find_packages

install_reqs = [req for req in open(join(dirname(__file__), 'requirements.txt'))]

packages = find_packages()

setup(
    name="raireplay",
    author='Audetto',
    version="1.0.0",
    license='GPL3',
    install_requires=install_reqs,
    packages=packages,
    url="https://github.com/audetto/raireplay",
    description="RaiPlay video download",
    python_requires='>=3.6'
)
