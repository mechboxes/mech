# Copyright (c) 2020 Mike Kinney

"""Mech integration tests"""
import re
import subprocess


import pytest


@pytest.mark.int
def test_version():
    """Test '--version'."""
    return_value, out = subprocess.getstatusoutput('mech --version')
    assert re.match(r'mech v[0-9]+\.[0-9]+\.[0-9]', out)
    assert return_value == 0


@pytest.mark.int
def test_help():
    """Test '--help'."""
    return_value, out = subprocess.getstatusoutput('mech --help')
    assert re.match(r'Usage: mech ', out)
    assert return_value == 0


@pytest.mark.int
def test_int_add_and_remove_instances():
    """Test add and remove instances integration tests."""
    return_value, out = subprocess.getstatusoutput(
        'cd tests/int && ./add_and_remove_instances.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_quick():
    """Test quick integration tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./quick.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_no_mechfile():
    """Test no_mechfile integration tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./no_mechfile.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_simple():
    """Test simple integration tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./simple.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_two_ubuntu():
    """Test two_ubuntu tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./two_ubuntu.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_init_from_file():
    """Test init_from_file tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./init_from_file.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_provision():
    """Test provision tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./provision.bats')
    assert return_value == 0


@pytest.mark.int
def test_int_shared_folders():
    """Test shared_folders tests."""
    return_value, out = subprocess.getstatusoutput('cd tests/int && ./shared_folders.bats')
    assert return_value == 0
