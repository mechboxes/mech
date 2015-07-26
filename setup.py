from setuptools import setup

setup(
    name='hobo',
    packages=['hobo'],
    entry_points={
        'console_scripts': [
            'hobo = hobo.__main__:main'
        ]
    },
    install_requires=['clint'],
    version='0.1',
    description='Tool for command line virtual machines',
    author='Kevin Chung',
    author_email='kchung@nyu.edu',
    url='https://github.com/ColdHeat/hobo',
    download_url='https://github.com/ColdHeat/hobo/tarball/0.1',
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[],
)
