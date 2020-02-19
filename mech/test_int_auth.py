# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: auth tests"""
import re
import subprocess

import pytest


@pytest.mark.int
def test_int_auth(helpers):
    """Auth testing."""

    test_dir = "tests/int/auth"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    # "up" with "add-me" and "use-me" options
    command = "mech init -a -u bento/ubuntu-18.04"
    expected_lines = [r"init"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # "list" detailed view shows psk
    command = "mech ls -d"
    expected_lines = [r"id_rsa.pub"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # "up" with 'remove-vagrant' option
    command = "mech up -r"
    expected_lines = [r"started", "Removing"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # make sure we can run a command using our psk (but do not
    # add entry to our known hosts file)
    command = """first_ip=`mech ip first`;
         ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
-o LogLevel=QUIET ${first_ip} -C uptime"""
    expected_lines = [r"load average"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

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
