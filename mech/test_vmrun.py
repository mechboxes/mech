# Copyright (c) 2020 Mike Kinney

"""Tests for VMrun class."""

from unittest.mock import patch, MagicMock, mock_open

import mech.vmrun


@patch('mech.vmrun.VMrun.vmrun', return_value='')
def test_vmrun_start(mock_vmrun):
    """Test start method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws')
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
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx',
                             executable='/tmp/vmrun', provider='ws')
    got = vmrun.vmrun('list', vmrun.vmx_file)
    assert got is None
    mock_popen.assert_called()


@patch('mech.vmrun.VMrun.vmrun', return_value='192.168.1.200')
def test_vmrun_get_guest_ip_address_no_lookup(mock_vmrun):
    """Test get_guest_ip_address method without lookup."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx',
                             executable='/tmp/vmrun', provider='ws')
    got = vmrun.get_guest_ip_address()
    assert got == '192.168.1.200'
    mock_vmrun.assert_called()


@patch('mech.vmrun.VMrun.vmrun', return_value='unknown')
def test_vmrun_get_guest_ip_address_no_lookup_unknown(mock_vmrun):
    """Test get_guest_ip_address method without lookup."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx',
                             executable='/tmp/vmrun', provider='ws')
    got = vmrun.get_guest_ip_address()
    assert got == ''
    mock_vmrun.assert_called()


@patch('mech.vmrun.VMrun.copy_file_from_guest_to_host', return_value='')
@patch('mech.vmrun.VMrun.run_script_in_guest', return_value='')
def test_vmrun_get_guest_ip_address_lookup(mock_run_script_in_guest,
                                           mock_copy_file_from_guest_to_host):
    """Test get_guest_ip_address method with lookup."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', user='auser', password='apass',
                             executable='/tmp/vmrun', provider='ws')
    a_mock = mock_open()
    a_mock = mock_open(read_data='192.168.1.201')
    with patch('builtins.open', a_mock, create=True):
        got = vmrun.get_guest_ip_address(lookup=True)
        assert got == '192.168.1.201'
    a_mock.assert_called()
    mock_run_script_in_guest.assert_called()
    mock_copy_file_from_guest_to_host.assert_called()
