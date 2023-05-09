from setuptools import setup, find_packages

setup(
    name='elasticsearch-indexer',
    packages=['elasticsearch_indexer'],
    version='0.0.3',
    author="Develper Junio",
    author_email='developer@junio.in',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    description="Thread based bulk writer for elasticsearch",
    license="MIT license",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "elasticsearch == 7.14.0",
        "structlog == 23.1.0"
    ]
)
