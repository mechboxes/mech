"""Test the mech cli. """
import subprocess
import re

from unittest.mock import patch

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


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('mech.vmrun.VMrun.listPortForwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.listHostNetworks', return_value=HOST_NETWORKS)
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


HOST_NETWORKS = """Total host networks: 3
INDEX  NAME         TYPE         DHCP         SUBNET           MASK
0      vmnet0       bridged      false        empty            empty
1      vmnet1       hostOnly     true         172.16.11.0      255.255.255.0
8      vmnet8       nat          true         192.168.3.0      255.255.255.0"""
@patch('mech.vmrun.VMrun.listPortForwardings', return_value='Total port forwardings: 0')
@patch('mech.vmrun.VMrun.listHostNetworks', return_value=HOST_NETWORKS)
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
@patch('mech.vmrun.VMrun.listHostNetworks', return_value=HOST_NETWORKS_WITHOUT_NAT)
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
