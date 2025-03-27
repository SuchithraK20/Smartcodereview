from setuptools import setup, find_packages

setup(
    name='Smartcodereview',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # list your project dependencies here
    ],
    entry_points={
        'console_scripts': [
            'smartcodereview = smartcodereview.main:main',
        ],
    },
)