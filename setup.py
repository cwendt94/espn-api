from setuptools import setup

setup(
    setup_requires=["nose>=1.0"],
    test_suite="nose.collector",
    tests_require=["nose", "requests_mock", "coverage"],
)
