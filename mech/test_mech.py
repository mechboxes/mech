"""Test the mech cli. """
import subprocess
import re
import json

from unittest.mock import patch, mock_open
from pytest import raises

import mech.command
import mech.mech
import mech.vmrun


def test_version():
    """Test '--version'."""
    return_value, out = subprocess.getstatusoutput('mech --version')
    assert re.match(r'mech v[0-9]+\.[0-9]+\.[0-9]', out)
    assert return_value == 0


def test_help():
    """Test '--help'."""
    return_value, out = subprocess.getstatusoutput('mech --help')
    assert re.match(r'Usage: mech ', out)
    assert return_value == 0


MECHFILE_ONE_ENTRY = {
    'first': {
        'name':
        'first',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0'
    }
}
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech list' with one entry."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one_and_debug(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech list' with one entry."""
    global_arguments = {'--debug': True}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': True}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'created:False', out, re.MULTILINE)


MECHFILE_TWO_ENTRIES = {
    'first': {
        'name':
        'first',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0',
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
        'versions/201912.04.0/providers/vmware_desktop.box'
    },
    'second': {
        'name':
        'second',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0',
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
        'versions/201912.04.0/providers/vmware_desktop.box'
    }
}
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_two(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech list' with two entries."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    a_mech.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)
    assert re.search(r'second\s+notcreated', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value=None)
def test_mech_status_with_two_not_created(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech status' with two entries, neither created."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {'<instance>': None}
    a_mech.status(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first.*has not been created', out, re.MULTILINE)
    assert re.search(r'second.*has not been created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.check_tools_state', return_value="running")
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_status_powered_on(mock_locate, mock_load_mechfile,
                                mock_get_ip, mock_check_tools_state, capfd):
    """Test 'mech status' powered on."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {'<instance>': 'first'}
    a_mech.status(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_get_ip.assert_called()
    mock_check_tools_state.assert_called()
    assert re.search(r'VM is ready', out, re.MULTILINE)


@patch('os.path.exists', return_value=True)
@patch('shutil.rmtree')
@patch('mech.vmrun.VMrun.delete_vm')
@patch('mech.vmrun.VMrun.stop', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_destroy(mock_locate, mock_load_mechfile,
                      mock_vmrun_stop, mock_vmrun_delete_vm,
                      mock_rmtree, mock_path_exists, capfd):
    """Test 'mech destroy' powered on."""
    mock_rmtree.return_value = True
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': True,
    }
    a_mech.destroy(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    mock_vmrun_delete_vm.assert_called()
    mock_rmtree.assert_called()
    mock_path_exists.assert_called()
    assert re.search(r'Deleting', out, re.MULTILINE)
    assert re.search(r'Deleted', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.vmrun.VMrun.stop', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_stop(mock_locate, mock_load_mechfile,
                   mock_vmrun_stop, mock_installed_tools,
                   capfd):
    """Test 'mech stop' powered on."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.down(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    mock_installed_tools.assert_called()
    assert re.search(r'Stopped', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.pause', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_pause(mock_locate, mock_load_mechfile,
                    mock_vmrun_stop, capfd):
    """Test 'mech stop' powered on."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--force': None,
    }
    a_mech.pause(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_stop.assert_called()
    assert re.search(r'Paused', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value='192.168.1.101')
@patch('mech.vmrun.VMrun.unpause', return_value=True)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
def test_mech_resume(mock_locate, mock_load_mechfile,
                     mock_vmrun_unpause, mock_vmrun_get_ip,
                     capfd):
    """Test 'mech resume'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
        '--disable-shared-folders': True,
        '--force': True,
    }
    a_mech.resume(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_vmrun_unpause.assert_called()
    mock_vmrun_get_ip.assert_called()
    assert re.search(r'resumed', out, re.MULTILINE)


MECHFILE_BAD_ENTRY = {
    '': {
        'name':
        '',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0'
    }
}
@patch('mech.utils.load_mechfile', return_value=MECHFILE_BAD_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_up_without_name(mock_locate, mock_load_mechfile):
    """Test 'mech up' (overriding name to be '') to test exception."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--detail': False,
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': '',
    }
    with raises(AttributeError, match=r"Must provide a name for the instance."):
        a_mech.up(arguments)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_up_with_name_not_in_mechfile(mock_locate, mock_load_mechfile):
    """Test 'mech up' with a name that is not in the Mechfile."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--detail': False,
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': 'notfirst',
    }
    with raises(SystemExit, match=r" was not found in the Mechfile"):
        a_mech.up(arguments)


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.init_box', return_value='/tmp/first/one.vmx')
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_already_started(mock_locate, mock_load_mechfile, mock_init_box,
                                 mock_vmrun_start, mock_vmrun_get_ip, capfd):
    """Test 'mech up'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': None,
    }
    a_mech.up(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_init_box.assert_called()
    mock_vmrun_start.assert_called()
    mock_vmrun_get_ip.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'\)started on', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.vmrun.VMrun.start', return_value=None)
@patch('mech.utils.init_box', return_value='/tmp/first/one.vmx')
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_problem(mock_locate, mock_load_mechfile, mock_init_box,
                         mock_vmrun_start, mock_vmrun_get_ip, capfd):
    """Test 'mech up' when issue with starting VM"""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': True,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': None,
    }
    a_mech.up(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_init_box.assert_called()
    mock_vmrun_start.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'not started', out, re.MULTILINE)


@patch('mech.utils.provision')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.init_box', return_value='/tmp/first/one.vmx')
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_with_provisioning(mock_locate, mock_load_mechfile, mock_init_box,
                                   mock_vmrun_start, mock_vmrun_get_ip,
                                   mock_provision, capfd):
    """Test 'mech up'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': True,
        '--disable-provisioning': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': None,
    }
    a_mech.up(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_init_box.assert_called()
    mock_vmrun_start.assert_called()
    mock_vmrun_get_ip.assert_called()
    mock_provision.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'started', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.add_shared_folder')
@patch('mech.vmrun.VMrun.enable_shared_folders')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value="192.168.1.100")
@patch('mech.vmrun.VMrun.start', return_value=True)
@patch('mech.utils.init_box', return_value='/tmp/first/one.vmx')
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
def test_mech_up_wth_shared_folders(mock_locate, mock_load_mechfile, mock_init_box,
                                    mock_vmrun_start, mock_vmrun_get_ip,
                                    mock_vmrun_enable_shared_folders,
                                    mock_vmrun_add_shared_folder, capfd):
    """Test 'mech up'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--gui': False,
        '--disable-shared-folders': False,
        '--disable-provisioning': True,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--checksum': None,
        '--checksum-type': None,
        '--no-cache': None,
        '--memsize': None,
        '--numvcpus': None,
        '<instance>': None,
    }
    a_mech.up(arguments)
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_init_box.assert_called()
    mock_vmrun_start.assert_called()
    mock_vmrun_get_ip.assert_called()
    mock_vmrun_enable_shared_folders.assert_called()
    mock_vmrun_add_shared_folder.assert_called()
    out, _ = capfd.readouterr()
    assert re.search(r'started', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_ssh_config_not_created(mock_locate, mock_load_mechfile, capfd):
    """Test 'mech ssh-config' when vm is not created."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.ssh_config(arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value=None)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
@patch('os.getcwd')
def test_mech_ssh_config_not_started(mock_getcwd, mock_locate, mock_load_mechfile,
                                     mock_get_guest_ip_address):
    """Test 'mech ssh-config' when vm is created but not started."""
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    with raises(SystemExit, match=r".*not yet ready for SSH.*"):
        a_mech.ssh_config(arguments)


@patch('os.chmod')
@patch('mech.vmrun.VMrun.installed_tools', return_value='running')
@patch('mech.vmrun.VMrun.get_guest_ip_address', return_value='192.168.2.120')
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value='/tmp/first/some.vmx')
@patch('os.getcwd')
def test_mech_ssh_config(mock_getcwd, mock_locate,  # pylint: disable=too-many-arguments
                         mock_load_mechfile, mock_get_guest_ip_address,
                         mock_installed_tools, mock_chmod, capfd):
    """Test 'mech ssh-config'."""
    mock_getcwd.return_value = '/tmp'
    mock_chmod.return_value = 0
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    mock_file = mock_open()
    with patch('builtins.open', mock_file, create=True):
        a_mech.ssh_config(arguments)
        out, _ = capfd.readouterr()
        mock_locate.assert_called()
        mock_load_mechfile.assert_called()
        mock_get_guest_ip_address.assert_called()
        mock_installed_tools.assert_called()
        mock_file.assert_called()
        mock_chmod.assert_called()
        assert re.search(r'Host first', out, re.MULTILINE)
        assert re.search(r'  User vagrant', out, re.MULTILINE)
        assert re.search(r'  Port 22', out, re.MULTILINE)


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat(mock_locate, mock_load_mechfile, mock_list_host_networks,
                            mock_list_port_forwardings, capfd):
    """Test 'mech port' with nat networking."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_and_instance(mock_locate, mock_load_mechfile, mock_list_host_networks,
                                         mock_list_port_forwardings, capfd):
    """Test 'mech port first' with nat networking."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': 'first'}
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('mech.vmrun.VMrun.list_port_forwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value=None)
def test_mech_port_with_nat_two_hosts(mock_locate, mock_load_mechfile, mock_list_host_networks,
                                      mock_list_port_forwardings, capfd):
    """Test 'mech port' with nat networking and two instances."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mech.port(port_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    mock_list_port_forwardings.assert_called()
    assert re.search(r'Total port forwardings: 0', out, re.MULTILINE)


HOST_NETWORKS_WITHOUT_NAT = """Total host networks: 2
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0"""
@patch('mech.vmrun.VMrun.list_host_networks', return_value=HOST_NETWORKS_WITHOUT_NAT)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('mech.utils.locate', return_value=None)
def test_mech_port_without_nat(mock_locate, mock_load_mechfile, mock_list_host_networks, capfd):
    """Test 'mech port' without nat."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    port_arguments = {}
    port_arguments = {'<instance>': None}
    a_mech.port(port_arguments)
    _, err = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_host_networks.assert_called()
    assert re.search(r'Cannot find a nat network', err, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init(mock_os_getcwd, mock_os_path_exists,
                   mock_requests_get, capfd):
    """Test 'mech init' from Hashicorp'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = False
    global_arguments = {'--debug': False}
    catalog = """{
        "description": "foo",
        "short_description": "foo",
        "name": "bento/ubuntu-18.04",
        "versions": [
            {
                "version": "aaa",
                "status": "active",
                "description_html": "foo",
                "description_markdown": "foo",
                "providers": [
                    {
                        "name": "vmware_desktop",
                        "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box",
                        "checksum": null,
                        "checksum_type": null
                    }
                ]
            }
        ]
    }"""
    catalog_as_json = json.loads(catalog)
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json

    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--force': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '--name': None,
        '--box': None,
        '<location>': 'bento/ubuntu-18.04',
    }
    a_mech.init(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'Loading metadata', out, re.MULTILINE)


@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init_mechfile_exists(mock_os_getcwd, mock_os_path_exists):
    """Test 'mech init' when Mechfile exists'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = True
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--force': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '--name': None,
        '--box': None,
        '<location>': 'bento/ubuntu-18.04',
    }
    with raises(SystemExit, match=r".*already exists in this directory.*"):
        a_mech.init(arguments)


@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_init_with_invalid_location(mock_os_getcwd, mock_os_path_exists):
    """Test if we do not have a valid location. (must be in form of 'hashiaccount/boxname')."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = False
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--force': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '--name': None,
        '--box': None,
        '<location>': 'bento',
    }
    with raises(SystemExit, match=r"Provided box name is not valid"):
        a_mech.init(arguments)


@patch('requests.get')
@patch('os.getcwd')
def test_mech_add_mechfile_exists(mock_os_getcwd,
                                  mock_requests_get, capfd):
    """Test 'mech add' when Mechfile exists'."""
    mock_os_getcwd.return_value = '/tmp'
    catalog = """{
        "description": "foo",
        "short_description": "foo",
        "name": "bento/ubuntu-18.04",
        "versions": [
            {
                "version": "aaa",
                "status": "active",
                "description_html": "foo",
                "description_markdown": "foo",
                "providers": [
                    {
                        "name": "vmware_desktop",
                        "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box",
                        "checksum": null,
                        "checksum_type": null
                    }
                ]
            }
        ]
    }"""
    catalog_as_json = json.loads(catalog)
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '<name>': 'second',
        '--box': None,
        '<location>': 'bento/ubuntu-18.04',
    }
    a_mech.add(arguments)
    out, _ = capfd.readouterr()
    mock_os_getcwd.assert_called()
    assert re.search(r'Loading metadata', out, re.MULTILINE)


def test_mech_add_mechfile_exists_no_name():
    """Test 'mech add' when Mechfile exists but no name provided'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '<name>': None,
        '--box': None,
        '<location>': 'bento/ubuntu-18.04',
    }
    with raises(SystemExit, match=r".*Need to provide a name.*"):
        a_mech.add(arguments)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('os.getcwd')
def test_mech_remove(mock_os_getcwd, mock_load_mechfile, capfd):
    """Test 'mech remove'."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': 'first',
    }
    a_mech.remove(arguments)
    out, _ = capfd.readouterr()
    mock_os_getcwd.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'Removed', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_ONE_ENTRY)
@patch('os.getcwd')
def test_mech_remove_a_nonexisting_entry(mock_os_getcwd, mock_load_mechfile, capfd):
    """Test 'mech remove'."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': 'second',
    }
    with raises(SystemExit, match=r".*There is no instance.*"):
        a_mech.remove(arguments)


def test_mech_remove_no_name():
    """Test 'mech remove' no name provided'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<name>': None,
    }
    with raises(SystemExit, match=r".*Need to provide a name.*"):
        a_mech.remove(arguments)


@patch('mech.vmrun.VMrun.list', return_value="Total running VMs: 0")
def test_mech_global_status(mock_list, capfd):
    """Test 'mech global-status'."""
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {}
    a_mech.global_status(arguments)
    out, _ = capfd.readouterr()
    mock_list.assert_called()
    assert re.search(r'Total running VMs', out, re.MULTILINE)


PROCESSES = """Process list: 99
pid=1, owner=root, cmd=/sbin/init
pid=2, owner=root, cmd=kthreadd
pid=3, owner=root, cmd=rcu_gp
pid=4, owner=root, cmd=rcu_par_gp
pid=5, owner=root, cmd=kworker/0:0-events
pid=6, owner=root, cmd=kworker/0:0H-kblockd
"""
@patch('mech.vmrun.VMrun.list_processes_in_guest', return_value=PROCESSES)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='/tmp/first/one.vmx')
@patch('os.getcwd')
def test_mech_ps(mock_getcwd, mock_locate, mock_load_mechfile, mock_list_processes, capfd):
    """Test 'mech ps'."""
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'first',
    }
    a_mech.ps(arguments)
    out, _ = capfd.readouterr()
    mock_getcwd.assert_called()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    mock_list_processes.assert_called()
    assert re.search(r'kworker', out, re.MULTILINE)


@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('mech.utils.locate', return_value='')
@patch('os.getcwd')
def test_mech_ps_not_started_vm(mock_getcwd, mock_locate,
                                mock_load_mechfile, capfd):
    """Test 'mech ps'."""
    mock_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.Mech(arguments=global_arguments)
    arguments = {
        '<instance>': 'second',
    }
    a_mech.ps(arguments)
    out, _ = capfd.readouterr()
    mock_getcwd.assert_called()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'not created', out, re.MULTILINE)
