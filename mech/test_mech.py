"""Test the mech cli. """
import subprocess
import re

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
