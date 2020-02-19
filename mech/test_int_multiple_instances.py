# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: multiple instances"""
import re
import subprocess


import pytest


@pytest.mark.int
def test_int_multiple_instances(helpers):
    """Test with multiple instances."""

    test_dir = "tests/int/multiple_instances"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    mechfile_contents = """{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/201912.04.0/providers/vmware_desktop.box"
  },
  "second": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "second",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/201912.04.0/providers/vmware_desktop.box"
  }
}
    """
    mechfile_path = test_dir + '/' + 'Mechfile'
    mechfile_file = open(mechfile_path, "w")
    mechfile_file.write(mechfile_contents)
    mechfile_file.close()

    # list two
    command = "mech ls"
    expected_lines = ["first", "second"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should start
    command = "mech up"
    expected_lines = ["could not be found", "vmware_desktop",
                      "integrity", "Extracting", "Added network",
                      "Bringing machine", "Getting IP", "Sharing folders",
                      "started", "Provisioning"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    command = "mech add third bento/ubuntu-18.04"
    expected_lines = ["Adding", "Loading", "Added"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should stop one
    command = "mech stop first"
    expected_lines = ["Stopped"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should only have one instance running (second)
    command = "mech ls"
    expected_lines = [r"first.*poweroff",
                      r"second.*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                      r"third.*notcreated"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # should be able to destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)
