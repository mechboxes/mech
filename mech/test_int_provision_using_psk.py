# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: provisioning tests using psk"""
import re
import subprocess

import pytest


@pytest.mark.int
def test_int_provision_using_psk(helpers):
    """Provision testing using psk."""

    test_dir = "tests/int/provision_using_psk/tmp"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    # copy files from parent dir
    command = "cp ../file* .; cp ../Mechfile ."
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # up (and remove vagrant user)
    command = "mech up -r"
    expected_lines = [r".first.*started",
                      r".second.*started",
                      r".third.*started",
                      r"Added auth",
                      r"first.*Provision 2 entries",
                      r"second.*Provision 3 entries",
                      r"Nothing",
                      r"Removing username"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure file exists
    command = 'mech ssh -c "ls -al /tmp/file1.txt" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("/tmp/file1.txt", stdout)
    assert results.returncode == 0

    # destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # clean up at the end
    helpers.cleanup_dir_and_vms_from_dir(test_dir)
