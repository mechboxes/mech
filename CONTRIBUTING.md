# Contributing to mech 

Anyone can open a pull request to help expand/enhance the functionality are essential to mech's growth.

This guide should help get you started contributing to mech.


## Dev Setup

```sh
# Clone the repo
git clone git@github.com:mkinney/mech.git

# Change into that cloned directory
cd mech

# If virtualenv is not installed:
sudo apt-get install virtualenv

# Create a virtualenv
virtualenv -p python3 venv

# Activate the python virtual environment
source venv/bin/activate

# consider installing/using direnv (there is a .envrc in this repo)
# may need to run "direnv allow"

# install mech from this code
python setup.py install

# if doing development
pip install docopt clint requests flake8 pytest pytest_mock mock pytest-cov pylint pytest-xdist pytest-timeout

# also optional
pip install autopep8
# use like this: autopep8 --in-place --aggressive --aggressive somefile.py

# Configure git to use pre-commit hook
flake8 --install-hook git

# for running unit tests:
pytest

# for code coverage
pytest --cov mech

# to see what lines are not covered
pytest --cov-report term-missing --cov mech

# or to get a nice html output
pytest --cov-report html:cov_html --cov=mech
# then open cov_html/index.html
# or if you want all coverage html report
pytest --cov-report html:cov_html --cov=mech -m"int or not int"

# if you want to do a quick-ish (takes 1.5 minutes) smoke test
# this runs thru most basic functionality of mech
./smoke_test

# to see the slowest unit tests
pytest --durations=0

# if you have a unittest that is taking too long, but cannot find out which one
# add "timeout = 10" (for 10 seconds)

# for testing/validation, we have also some integration tests
# NOTE: Can take 5+ minutes.
# cd tests/int (see "all" file)
# You can run the int tests by themselves directly if you change
# into the tests/int directory.
# Or, you can run them from the main project directory like this:
pytest -m"int"

# To run all tests (with verbose output and show local variables):
pytest -m"int or not int" -vv -l
# or just run "./full_test"

# Or, just one run int test like this (with verbose and show local variables):
pytest -m"int" -k"provision" -v -l
```
