from setuptools import setup

setup(
    name='mech',
    packages=['mech'],
    entry_points={
        'console_scripts': [
            'mech = mech.__main__:main'
        ]
    },
    install_requires=['requests', 'clint', 'docopt', 'filelock'],
    version='0.6',
    description='Tool for command line virtual machines',
    author='Kevin Chung',
    author_email='kchung@nyu.edu',
    url='https://github.com/mechboxes/mech',
    download_url='https://github.com/mechboxes/mech/tarball/master',
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[],
)
