# Copyright (c) 2020 Mike Kinney

"""Tests for VMrun class."""

from unittest.mock import patch, MagicMock, mock_open

import mech.vmrun


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


def test_vmrun_start():
    """Test start method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'start', '/tmp/first/some.vmx', 'nogui']
    got = vmrun.start()
    assert got == expected


def test_vmrun_stop():
    """Test stop method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'stop', '/tmp/first/some.vmx', 'soft']
    got = vmrun.stop()
    assert got == expected


def test_vmrun_reset():
    """Test reset method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'reset', '/tmp/first/some.vmx', 'soft']
    got = vmrun.reset()
    assert got == expected


def test_vmrun_suspend():
    """Test suspend method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'suspend', '/tmp/first/some.vmx', 'soft']
    got = vmrun.suspend()
    assert got == expected


def test_vmrun_pause():
    """Test pause method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'pause', '/tmp/first/some.vmx']
    got = vmrun.pause()
    assert got == expected


def test_vmrun_unpause():
    """Test unpause method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'unpause', '/tmp/first/some.vmx']
    got = vmrun.unpause()
    assert got == expected


def test_vmrun_list_snapshots():
    """Test list_snapshots method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listSnapshots', '/tmp/first/some.vmx']
    got = vmrun.list_snapshots()
    assert got == expected


def test_vmrun_snapshot():
    """Test snapshot method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'snapshot', '/tmp/first/some.vmx', 'snap1']
    got = vmrun.snapshot('snap1')
    assert got == expected


def test_vmrun_delete_snapshot():
    """Test delete_snapshot method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deleteSnapshot', '/tmp/first/some.vmx', 'snap1']
    got = vmrun.delete_snapshot('snap1')
    assert got == expected


def test_vmrun_revert_to_snapshot():
    """Test revert_to_snapshot method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'revertToSnapshot', '/tmp/first/some.vmx', 'snap2']
    got = vmrun.revert_to_snapshot('snap2')
    assert got == expected


def test_vmrun_list_network_adapters():
    """Test list_network_adapters method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listNetworkAdapters', '/tmp/first/some.vmx']
    got = vmrun.list_network_adapters('snap2')
    assert got == expected


def test_vmrun_add_network_adapter():
    """Test add_network_adapter method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'addNetworkAdapter', '/tmp/first/some.vmx', 'a_type']
    got = vmrun.add_network_adapter('a_type')
    assert got == expected


def test_vmrun_set_network_adapter():
    """Test set_network_adapter method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'setNetworkAdapter',
                '/tmp/first/some.vmx', 'some_index', 'a_type']
    got = vmrun.set_network_adapter('some_index', 'a_type')
    assert got == expected


def test_vmrun_delete_network_adapter():
    """Test delete_network_adapter method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deleteNetworkAdapter', '/tmp/first/some.vmx', 'a_type']
    got = vmrun.delete_network_adapter('a_type')
    assert got == expected


def test_vmrun_list_networks():
    """Test list_host_networks method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listHostNetworks']
    got = vmrun.list_host_networks()
    assert got == expected


def test_vmrun_list_port_forwardings():
    """Test list_port_forwardings method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listPortForwardings', 'a_host_network']
    got = vmrun.list_port_forwardings('a_host_network')
    assert got == expected


def test_vmrun_set_port_forwarding():
    """Test set_port_forwarding method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'setPortForwarding',
                'a_host_network', 'a_protocol', 'a_host_port', 'a_guest_ip', 'a_guest_port']
    got = vmrun.set_port_forwarding('a_host_network', 'a_protocol',
                                    'a_host_port', 'a_guest_ip', 'a_guest_port')
    assert got == expected


def test_vmrun_delete_port_forwarding():
    """Test delete_port_forwarding method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deletePortForwarding',
                'a_host_network', 'a_protocol', 'a_host_port']
    got = vmrun.delete_port_forwarding('a_host_network', 'a_protocol', 'a_host_port')
    assert got == expected


def test_vmrun_run_program_in_guest():
    """Test run_program_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'runProgramInGuest', '/tmp/first/some.vmx',
                'program_path', 'one_cmd']
    got = vmrun.run_program_in_guest('program_path', ['one_cmd'])
    assert got == expected


def test_vmrun_run_program_in_guest_non_defaults():
    """Test run_program_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'runProgramInGuest', '/tmp/first/some.vmx',
                '-noWait', '-activateWindow', '-interactive', 'program_path', 'one_cmd']
    got = vmrun.run_program_in_guest('program_path', ['one_cmd'], wait=False,
                                     activate_window=True, interactive=True)
    assert got == expected


def test_vmrun_set_shared_folder_state():
    """Test set_shared_folder_state method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'setSharedFolderState', '/tmp/first/some.vmx',
                'a_share_name', 'a_new_path', 'readonly']
    got = vmrun.set_shared_folder_state('a_share_name', 'a_new_path')
    assert got == expected


def test_vmrun_add_shared_folder():
    """Test add_shared_folder method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'addSharedFolder', '/tmp/first/some.vmx',
                'a_share_name', 'a_path']
    got = vmrun.add_shared_folder('a_share_name', 'a_path')
    assert got == expected


def test_vmrun_remove_shared_folder():
    """Test remove_shared_folder method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'removeSharedFolder', '/tmp/first/some.vmx',
                'a_share_name']
    got = vmrun.remove_shared_folder('a_share_name')
    assert got == expected


def test_vmrun_enable_shared_folders():
    """Test enable_shared_folders method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'enableSharedFolders', '/tmp/first/some.vmx']
    got = vmrun.enable_shared_folders()
    assert got == expected


def test_vmrun_disable_shared_folders():
    """Test disable_shared_folders method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'disableSharedFolders', '/tmp/first/some.vmx']
    got = vmrun.disable_shared_folders()
    assert got == expected


def test_vmrun_list_processes_in_guest():
    """Test list_processes_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listProcessesInGuest', '/tmp/first/some.vmx']
    got = vmrun.list_processes_in_guest()
    assert got == expected


def test_vmrun_kill_process_in_guest():
    """Test kill_process_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'killProcessInGuest', '/tmp/first/some.vmx', 'a_pid']
    got = vmrun.kill_process_in_guest('a_pid')
    assert got == expected


def test_vmrun_run_script_in_guest():
    """Test run_script_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'runScriptInGuest', '/tmp/first/some.vmx',
                'a_path', 'a_script']
    got = vmrun.run_script_in_guest('a_path', 'a_script')
    assert got == expected


def test_vmrun_delete_file_in_guest():
    """Test delete_file_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deleteFileInGuest', '/tmp/first/some.vmx', 'a_file']
    got = vmrun.delete_file_in_guest('a_file')
    assert got == expected


def test_vmrun_create_directory_in_guest():
    """Test create_directory_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'createDirectoryInGuest', '/tmp/first/some.vmx', 'a_dir']
    got = vmrun.create_directory_in_guest('a_dir')
    assert got == expected


def test_vmrun_delete_directory_in_guest():
    """Test delete_directory_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deleteDirectoryInGuest', '/tmp/first/some.vmx', 'a_dir']
    got = vmrun.delete_directory_in_guest('a_dir')
    assert got == expected


def test_vmrun_create_tempfile_in_guest():
    """Test create_tempfile_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'createTempfileInGuest', '/tmp/first/some.vmx']
    got = vmrun.create_tempfile_in_guest()
    assert got == expected


def test_vmrun_list_directory_in_guest():
    """Test list_directory_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listDirectoryInGuest', '/tmp/first/some.vmx', 'a_path']
    got = vmrun.list_directory_in_guest('a_path')
    assert got == expected


def test_vmrun_copy_file_from_host_to_guest():
    """Test copy_file_from_host_to_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'copyFileFromHostToGuest', '/tmp/first/some.vmx',
                'a_host_path', 'a_guest_path']
    got = vmrun.copy_file_from_host_to_guest('a_host_path', 'a_guest_path')
    assert got == expected


def test_vmrun_copy_file_from_guest_to_host():
    """Test copy_file_from_guest_to_host method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'copyFileFromGuestToHost', '/tmp/first/some.vmx',
                'a_guest_path', 'a_host_path']
    got = vmrun.copy_file_from_guest_to_host('a_guest_path', 'a_host_path')
    assert got == expected


def test_vmrun_rename_file_in_guest():
    """Test rename_file_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'renameFileInGuest', '/tmp/first/some.vmx',
                'orig', 'new']
    got = vmrun.rename_file_in_guest('orig', 'new')
    assert got == expected


def test_vmrun_type_keystrokes_in_guest():
    """Test type_keystrokes_in_guest method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'typeKeystrokesInGuest', '/tmp/first/some.vmx',
                'some_keys']
    got = vmrun.type_keystrokes_in_guest('some_keys')
    assert got == expected


def test_vmrun_connect_named_device():
    """Test connect_named_device method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'connectNamedDevice', '/tmp/first/some.vmx',
                'a_device_name']
    got = vmrun.connect_named_device('a_device_name')
    assert got == expected


def test_vmrun_capture_screen():
    """Test capture_screen method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'captureScreen', '/tmp/first/some.vmx',
                'a_path_on_host']
    got = vmrun.capture_screen('a_path_on_host')
    assert got == expected


def test_vmrun_write_variable():
    """Test write_variable method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'writeVariable', '/tmp/first/some.vmx',
                'a_name', 'a_value']
    got = vmrun.write_variable('a_name', 'a_value')
    assert got == expected


def test_vmrun_read_variable():
    """Test read_variable method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'readVariable', '/tmp/first/some.vmx', 'a_name']
    got = vmrun.read_variable('a_name')
    assert got == expected


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


def test_vmrun_list():
    """Test list method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'list', '/tmp/first/some.vmx']
    got = vmrun.list()
    assert got == expected


def test_vmrun_upgradevm():
    """Test upgradevm method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'upgradevm', '/tmp/first/some.vmx']
    got = vmrun.upgradevm()
    assert got == expected


def test_vmrun_install_tools():
    """Test install_tools method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'installTools', '/tmp/first/some.vmx']
    got = vmrun.install_tools()
    assert got == expected


def test_vmrun_check_tools_state():
    """Test check_tools_state method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'checkToolsState', '/tmp/first/some.vmx']
    got = vmrun.check_tools_state()
    assert got == expected


def test_vmrun_register():
    """Test register method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'register', '/tmp/first/some.vmx']
    got = vmrun.register()
    assert got == expected


def test_vmrun_unregister():
    """Test unregister method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'unregister', '/tmp/first/some.vmx']
    got = vmrun.unregister()
    assert got == expected


def test_vmrun_list_registered_vm():
    """Test list_registered_vm method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'listRegisteredVM', '/tmp/first/some.vmx']
    got = vmrun.list_registered_vm()
    assert got == expected


def test_vmrun_delete_vm():
    """Test delete_vm method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'deleteVM', '/tmp/first/some.vmx']
    got = vmrun.delete_vm()
    assert got == expected


def test_vmrun_clone():
    """Test clone method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'clone', '/tmp/first/some.vmx',
                'a_dest_vmx', 'a_mode']
    got = vmrun.clone('a_dest_vmx', 'a_mode')
    assert got == expected


def test_vmrun_begin_recording():
    """Test begin_recording method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'beginRecording', '/tmp/first/some.vmx', 'a_name']
    got = vmrun.begin_recording('a_name')
    assert got == expected


def test_vmrun_end_recording():
    """Test end_recording method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'endRecording', '/tmp/first/some.vmx']
    got = vmrun.end_recording()
    assert got == expected


def test_vmrun_begin_replay():
    """Test begin_replay method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'beginReplay', '/tmp/first/some.vmx', 'a_name']
    got = vmrun.begin_replay('a_name')
    assert got == expected


def test_vmrun_end_replay():
    """Test end_replay method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'endReplay', '/tmp/first/some.vmx']
    got = vmrun.end_replay()
    assert got == expected


def test_vmrun_vprobe_version():
    """Test vprobe_version method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeVersion', '/tmp/first/some.vmx']
    got = vmrun.vprobe_version()
    assert got == expected


def test_vmrun_vprobe_load():
    """Test vprobe_load method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeLoad', '/tmp/first/some.vmx', 'a_script']
    got = vmrun.vprobe_load('a_script')
    assert got == expected


def test_vmrun_vprobe_load_file():
    """Test vprobe_load_file method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeLoadFile', '/tmp/first/some.vmx', 'a_script']
    got = vmrun.vprobe_load_file('a_script')
    assert got == expected


def test_vmrun_vprobe_reset():
    """Test vprobe_reset method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeReset', '/tmp/first/some.vmx']
    got = vmrun.vprobe_reset()
    assert got == expected


def test_vmrun_vprobe_list_probes():
    """Test vprobe_list_probes method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeListProbes', '/tmp/first/some.vmx']
    got = vmrun.vprobe_list_probes()
    assert got == expected


def test_vmrun_vprobe_list_globals():
    """Test vprobe_list_globals method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    expected = ['/tmp/vmrun', '-T', 'ws', 'vprobeListGlobals', '/tmp/first/some.vmx']
    got = vmrun.vprobe_list_globals()
    assert got == expected


@patch('mech.vmrun.VMrun.check_tools_state', return_value='')
def test_vmrun_installed_tools_not_running(mock_tools_state):
    """Test installed_tools method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    assert not vmrun.check_tools_state()


@patch('mech.vmrun.VMrun.check_tools_state', return_value='running')
def test_vmrun_installed_tools_running(mock_tools_state):
    """Test installed_tools method."""
    vmrun = mech.vmrun.VMrun('/tmp/first/some.vmx', executable='/tmp/vmrun',
                             provider='ws', test_mode=True)
    assert vmrun.check_tools_state()
