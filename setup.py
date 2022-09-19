from setuptools import setup, find_packages

pkg_vars = dict()
with open('espn_api/_version.py') as f:
    exec(f.read(), pkg_vars)

with open("README.md") as f:
    readme = f.read()

setup(
    name='espn_api',
    packages=find_packages(),
    version=pkg_vars["__version__"],
    author='Christian Wendt',
    description='ESPN API',
    long_description=readme,
    long_description_content_type="text/markdown",
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
