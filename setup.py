from setuptools import setup, find_packages


setup(
    name='cubepress',
    version='0.1',
    description="CSV-based OLAP report generator",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='data olap cubes datacube reports reporting',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/cubepress',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'SQLAlchemy>=0.9.8',
        'messytables>=0.2.1',
        'click>=3.2',
        'normality>=0.1',
        'pyyaml>=3.11',
        'jtssql>=0.1',
        'datapackage>=0.5.3'
    ],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'cubepress = cubepress.cli:cli'
        ]
    }
)
