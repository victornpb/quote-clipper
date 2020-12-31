from setuptools import setup, find_packages

setup(
    name='quoteclipper',
    version='0.0.1',
    py_modules=['modules'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'moviepy',
    ],
    entry_points = {
        "console_scripts": [
            "quoteclipper = scripts.__main__:main",
        ]
    }
)
