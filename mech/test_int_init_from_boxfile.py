# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: init from box file"""
import re
import subprocess


import pytest


@pytest.mark.int
def test_int_init_from_boxfile(helpers):
    """Test mech init from .box file."""

    test_dir = "tests/int/init_from_boxfile"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    ubuntu = "ubuntu-18.04"
    box_file = "/tmp/{}.box".format(ubuntu)

    # download the file if we don't have it already
    # that way we "cache" the file
    commands = """
    if ! [ -f "{box_file}" ]; then
      wget -O "{box_file}" "https://vagrantcloud.com/bento/\
boxes/{ubuntu}/versions/201912.04.0/providers/vmware_desktop.box"
    fi
    """.format(box_file=box_file, ubuntu=ubuntu)
    results = subprocess.run(commands, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert results.returncode == 0

    # init from boxfile
    command = "mech init --box bento/{} file:{}".format(ubuntu, box_file)
    expected_lines = ["Initializing", "has been init"]
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
    expected_lines = ["Extracting", "Added network",
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

    # should be able to destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)
