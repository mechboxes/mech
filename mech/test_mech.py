"""Test the mech cli. """
import subprocess
import re

from unittest.mock import patch

import mech.command
import mech.mech
import mech.vmrun


def test_version():
    rc, out = subprocess.getstatusoutput('mech --version')
    assert re.match(r'mech v[0-9]+\.[0-9]+\.[0-9]', out)
    assert rc == 0


def test_help():
    rc, out = subprocess.getstatusoutput('mech --help')
    assert re.match(r'Usage: mech ', out)
    assert rc == 0


mechfile_one_entry = {
    'first': {
        'name':
        'first',
        'box':
        'bento/ubuntu-18.04',
        'box_version':
        '201912.04.0'
    }
}
@patch('mech.utils.load_mechfile', return_value=mechfile_one_entry)
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_one(mock_locate, mock_load_mechfile, capfd):
    global_arguments = {'--debug': False}
    m = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    m.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)


mechfile_two_entries = {
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
@patch('mech.utils.load_mechfile', return_value=mechfile_two_entries)
@patch('mech.utils.locate', return_value=None)
def test_mech_list_with_two(mock_locate, mock_load_mechfile, capfd):
    global_arguments = {'--debug': False}
    m = mech.mech.Mech(arguments=global_arguments)
    list_arguments = {'--detail': False}
    m.list(list_arguments)
    out, _ = capfd.readouterr()
    mock_locate.assert_called()
    mock_load_mechfile.assert_called()
    assert re.search(r'first\s+notcreated', out, re.MULTILINE)
    assert re.search(r'second\s+notcreated', out, re.MULTILINE)
