# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: init from json file"""
import re
import subprocess


import pytest


@pytest.mark.int
def test_int_init_from_jsonfile(helpers):
    """Test mech init from .json file."""

    test_dir = "tests/int/init_from_jsonfile"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    ubuntu = "ubuntu-18.04"

    jsonfile_contents = """{
    "description": "Bento Ubuntu box",
    "short_description": "ubuntu",
    "name": "bento/ubuntu-18.04",
    "versions": [
        {
            "version": "201912.04.0",
            "status": "active",
            "description_html": "Some html description",
            "description_markdown": "Some markdown description",
            "providers": [
                {
                    "name": "vmware_desktop",
                    "url":  "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/201912.04.0/providers/vmware_desktop.box",
                    "checksum": null,
                    "checksum_type": null
                }
            ]
        }
    ]
}"""

    jsonfile_name = "bento_1804.json"
    jsonfile_path = "{}/{}".format(test_dir, jsonfile_name)
    jsonfile_file = open(jsonfile_path, "w")
    jsonfile_file.write(jsonfile_contents)
    jsonfile_file.close()

    # init from jsonfile
    command = "mech init --box bento/{} file:{}".format(ubuntu, jsonfile_name)
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

    # should be able to destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # clean up file
    helpers.cleanup_dir_and_vms_from_dir(test_dir)
