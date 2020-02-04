# Integration tests for mech

This directory contains files for integration testing.
You can run them all by running `./all`.

# Notes:
1) Test must be run from this directory.
2) Tests *should* be able to be run concurrently. (but no promises)
3) If a test fails, there may be some vmx processes still running.
   You should be able to change to that directory's test and inspect
   the last state.
4) See [CONTRIBUTING](../../CONTRIBUTING.md) for getting setup to run tests.
5) These tests will take several minutes to run. They download
files from the internet and start up/stop/destroy VMs.

# Scripts

- `./init_from_file.bats` - create box from file
- `./no_mechfile.bats` - simple validations without a Mechfile
- `./provision.bats` - provision validation
- `./quick.bats` - quick validations (ex: help, version)
- `./simple.bats` - simple validations of most basic functionality
- `./two_ubuntu.bats` - validate two ubuntu instances
- `./shared_folders.bats` - validate shared folders functionality
