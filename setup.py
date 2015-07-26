from setuptools import setup

setup(
    name='mech',
    packages=['mech'],
    entry_points={
        'console_scripts': [
            'mech = mech.__main__:main'
        ]
    },
    install_requires=['clint'],
    version='0.1',
    description='Tool for command line virtual machines',
    author='Kevin Chung',
    author_email='kchung@nyu.edu',
    url='https://github.com/ColdHeat/mech',
    download_url='https://github.com/ColdHeat/mech/tarball/0.1',
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[],
)
