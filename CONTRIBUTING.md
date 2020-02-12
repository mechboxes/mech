# Contributing to mech 

Anyone can open a pull request to help expand/enhance the functionality are essential to mech's growth.

This guide should help get you started contributing to mech.


## Dev Setup

```sh
# Clone the repo
git clone git@github.com:mkinney/mech.git

# Change into that cloned directory
cd mech

# Create a virtualenv
virtualenv -p python3 venv

# Activate the python virtual environment
source venv/bin/activate

# consider installing/using direnv (there is a .envrc in this repo)
# may need to run "direnv allow"

# install mech from this code
python setup.py install

# if doing development
pip install flake8 pytest pytest_mock mock pytest-cov pylint pytest-xdist

# also optional
pip install autopep8
# use like this: autopep8 --in-place --aggressive --aggressive somefile.py

# Configure git to use pre-commit hook
flake8 --install-hook git

# install bats (on mac)
# see https://github.com/bats-core/bats-core
brew install bats-core

# for running unit tests:
pytest

# for code coverage
pytest --cov mech

# to see what lines are not covered
pytest --cov-report term-missing --cov mech

# to see the slowest tests
pytest --durations=0

# for testing/validation, we have also some integration tests
# cd tests/int (see "all" file)
# You can run the int tests by themselves directly if you change
# into the tests/int directory.
# Or, you can run them from the main project directory like this:
pytest -m"int"

# Or, just one run int test like this (with verbose and show local variables):
pytest -m"int" -k"provision" -v -l
```
