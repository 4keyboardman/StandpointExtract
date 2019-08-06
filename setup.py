import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="StandpointExtract",
    version="1.0.0",
    url="http://flask.pocoo.org/docs/tutorial/",
    license="BSD",
    maintainer="4keyboardman",
    maintainer_email="fyjun2071@163.com",
    description="新闻人物观点自动提取",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", 'sqlalchemy', 'werkzeug'],
    extras_require={"test": ["pytest", "coverage"]},
)
