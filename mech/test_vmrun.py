# Copyright (c) 2020 Mike Kinney

"""Tests for VMrun class."""

from unittest.mock import patch, MagicMock

import mech.vmrun


@patch('mech.vmrun.VMrun.vmrun', return_value='')
def test_vmrun_start(mock_vmrun):
    """Test start method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', user='auser', password='apass')
    got = vmrun.start()
    mock_vmrun.assert_called()
    assert got == ''


@patch('subprocess.Popen')
def test_vmrun_vmrun(mock_popen):
    """Test vmrun method."""
    process_mock = MagicMock()
    attrs = {'communicate.return_value': ('output', 'error')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', user='auser', password='apass')
    got = vmrun.vmrun('list', vmrun.vmx_file)
    assert got is None
    mock_popen.assert_called()
