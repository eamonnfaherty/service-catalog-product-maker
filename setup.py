import setuptools
import os

with open(os.path.abspath(__file__).replace('setup.py', 'README.md'), "r") as fh:
    long_description = fh.read()

with open(os.path.abspath(__file__).replace('setup.py', 'requirements.txt'), "r") as fh:
    requirements = fh.read().split("\n")

setuptools.setup(
    name="servicecatalog-product-maker",
    version="0.0.1",
    author="Eamonn Faherty",
    author_email="python-packages@designandsolve.co.uk",
    description="Helpers to make creating AWS Service Catalog products easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eamonnfaherty/service-catalog-product-maker",
    packages=setuptools.find_packages(),
    package_data={'servicecatalog_product_maker': ['*','*/*','*/*/*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'servicecatalog-product-maker = servicecatalog_product_maker.product_maker:cli'
        ]},
    install_requires=requirements,
)
