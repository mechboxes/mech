# Copyright (c) 2020 Mike Kinney

"""Mech integration tests: simple ones (including smoke)"""
import re
import subprocess

import pytest


@pytest.mark.int
def test_int_no_args():
    """Test without any args"""
    return_value, out = subprocess.getstatusoutput('mech')
    assert re.match(r'Usage: mech ', out)
    assert return_value == 1


@pytest.mark.int
def test_int_version():
    """Test '--version'."""
    return_value, out = subprocess.getstatusoutput('mech --version')
    assert re.match(r'mech v[0-9]+\.[0-9]+\.[0-9]', out)
    assert return_value == 0


@pytest.mark.int
def test_int_help():
    """Test '--help'."""
    return_value, out = subprocess.getstatusoutput('mech --help')
    assert re.match(r'Usage: mech ', out)
    assert return_value == 0


@pytest.mark.int
def test_int_no_mechfile(helpers):
    """Test when no Mechfile."""
    test_dir = "tests/int/no_mechfile"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)
    command = "mech ls"
    return_value, out = subprocess.getstatusoutput(command)
    assert re.search(r'Could not find a Mechfile', out)
    assert return_value == 1


@pytest.mark.int
def test_int_smoke(helpers):
    """Smoke test most options."""

    test_dir = "tests/int/simple"
    helpers.cleanup_dir_and_vms_from_dir(test_dir)

    # ensure we need to provide more args
    commands = ["mech box", "mech init", "mech ip", "mech ps", "mech scp", "mech snapshot",
                "mech snapshot save", "mech snapshot save snap1", "mech snapshot delete",
                "mech snapshot remove", "mech ssh"]
    expected = "Usage: mech "
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stdout == ''
        assert results.returncode == 1
        assert re.search(expected, stderr)

    # should init
    command = "mech init mrlesmithjr/alpine311"
    expected_lines = ["Initializing", "Loading metadata", "has been initialized", "mech up"]
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

    # ensure we get proper response from bad instance name
    commands = ["mech status first2", "mech ip first2"]
    expected = "was not found in the Mechfile"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stdout == ''
        assert results.returncode == 1
        assert re.search(expected, stderr)

    # should be able to re-up, verify 'start' alias works, too
    commands = ["mech up", "mech start"]
    expected_lines = ["Bringing machine", "Getting IP", "Sharing folders",
                      "was already started", "Provisioning"]
    for command in commands:
        results = subprocess.run(commands, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech ps'
    command = "mech ps first"
    expected_lines = ["/sbin/init"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech status'
    command = "mech status"
    expected_lines = ["first", "Tools running"]
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech global-status'
    command = "mech global-status"
    expected_lines = [test_dir + '/.mech/first/']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech list'
    commands = ["mech ls", "mech list"]
    expected_lines = ['first', 'alpine']
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech stop'
    command = "mech stop"
    expected_lines = ['Stopped']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech stop' again
    command = "mech stop"
    expected_lines = ['Not stopped']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert re.search('The virtual machine is not powered on', stderr, re.MULTILINE)
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech start'
    command = "mech start"
    expected_lines = ['started']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech pause'
    command = "mech pause"
    expected_lines = ['Paused']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech resume'
    command = "mech resume"
    expected_lines = ['resumed']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech suspend'
    command = "mech suspend"
    expected_lines = ['Suspended']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech resume' after suspend
    command = "mech resume"
    expected_lines = ['started']
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    for line in expected_lines:
        print(line)
        assert re.search(line, stdout, re.MULTILINE)

    # test 'mech ssh' (different forms)
    commands = ["mech ssh -c 'uptime' first", "mech ssh --command 'uptime' first"]
    expected_lines = ['load average']
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        for line in expected_lines:
            print(line)
            assert re.search(line, stdout, re.MULTILINE)

    # test 'mech scp' to guest
    command = "date > now; mech scp now first:/tmp"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # test 'mech scp' from guest
    command = "mech scp first:/tmp/now ."
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert stderr == ''
    assert results.returncode == 0

    # test 'mech ip first'
    command = "mech ip first"
    expected = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # test "mech port"
    command = "mech port"
    expected = "Total port forwardings: 0"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout, re.MULTILINE)

    # test "mech box list" (and alias)
    commands = ["mech box list", "mech box ls"]
    expected = r"alpine"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot list" (and alias)
    commands = ["mech snapshot list", "mech snapshot ls"]
    expected = "Total snapshots: 0"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot save"
    command = "mech snapshot save snap1 first"
    expected = "taken"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # test "mech snapshot save" with same args again
    command = "mech snapshot save snap1 first"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stdout == ''
    assert re.search('A snapshot with the name already exists', stderr)
    assert results.returncode == 1

    # test "mech snapshot list" (and alias) again (now that we have one)
    commands = ["mech snapshot list", "mech snapshot ls"]
    expected = "Total snapshots: 1"
    for command in commands:
        results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
        stdout = results.stdout.decode('utf-8')
        stderr = results.stderr.decode('utf-8')
        assert stderr == ''
        assert results.returncode == 0
        assert re.search(expected, stdout, re.MULTILINE)

    # test "mech snapshot delete"
    command = "mech snapshot delete snap1 first"
    expected = "deleted"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)

    # should be able to destroy
    command = "mech destroy -f"
    expected = "Deleting"
    results = subprocess.run(command, cwd=test_dir, shell=True, capture_output=True)
    stdout = results.stdout.decode('utf-8')
    stderr = results.stderr.decode('utf-8')
    assert stderr == ''
    assert results.returncode == 0
    assert re.search(expected, stdout)
