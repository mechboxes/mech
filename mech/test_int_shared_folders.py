# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: shared folders tests"""
import re
import subprocess

import pytest


@pytest.mark.int
def test_int_shared_folders(helpers):
    """Shared folders testing."""

    test_dir = "tests/int/shared_folders/tmp"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    # copy file from parent dir
    command = "cp ../Mechfile ."
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # up
    command = "mech up"
    expected_lines = [r"started"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure the Mechfile is present from the guest
    command = 'mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("Mechfile", stdout)
    assert results.returncode == 0

    # create a simple file to see if visible on another share
    command = 'date > /tmp/now'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # ensure we can see the file on the other share
    command = 'mech ssh -c "ls -al /mnt/hgfs/mech2/now" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("/mnt/hgfs/mech2/now", stdout)
    assert results.returncode == 0

    # stop
    command = "mech stop"
    expected_lines = [r"Stopped"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # "up" but do not have shared folders
    command = "mech up --disable-shared-folders"
    expected_lines = [r"started"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure the Mechfile is *NOT* present from the guest
    command = 'mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("No such file or directory", stdout)
    assert results.returncode == 2

    # pause
    command = "mech pause"
    expected_lines = [r"Paused"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # "resume" but do not have shared folders
    command = "mech resume --disable-shared-folders"
    expected_lines = ["resumed"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # ensure the Mechfile is *NOT* present from the guest
    command = 'mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first'
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert re.search("No such file or directory", stdout)
    assert results.returncode == 2

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
