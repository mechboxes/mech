# Integration tests for mech

This directory contains files for integration testing.

# Notes:
1) Test must be run from this directory.
2) Tests should be able to be run concurrently.
3) If a test fails, there may be some vmx processes still running.
4) See ../CONTRIBUTING.md for getting setup to run tests.
5) These tests will take several minutes to run. They download
files from the internet and start up/stop/destroy VMs.

# Scripts
./simple.bats - run some simple tests with Alpine image
./two_ubuntu.bats - validate two ubuntu instances work as expected
