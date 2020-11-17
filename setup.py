from setuptools import setup, find_packages

setup(
    name='espn_api',
    packages=find_packages(),
    version='0.8.3',
    author='Christian Wendt',
    description='ESPN API',
    install_requires=['requests>=2.0.0,<3.0.0'],
    setup_requires=['nose>=1.0'],
    test_suite='nose.collector',
    tests_require=['nose', 'requests_mock', 'coverage'],
    url='https://github.com/cwendt94/espn-api',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
