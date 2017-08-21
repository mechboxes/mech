from setuptools import setup

setup(
    name='mech',
    packages=['mech'],
    entry_points={
        'console_scripts': [
            'mech = mech.__main__:main'
        ]
    },
    install_requires=['requests', 'clint'],
    version='0.5',
    description='Tool for command line virtual machines',
    author='Kevin Chung',
    author_email='kchung@nyu.edu',
    url='https://github.com/ColdHeat/mech',
    download_url='https://github.com/ColdHeat/mech/tarball/master',
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[],
)
