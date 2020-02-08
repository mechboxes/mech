import os

from unittest.mock import patch, mock_open
from collections import OrderedDict

import mech.utils


@patch('os.getcwd')
def test_main_dir(mock_os_getcwd):
    mock_os_getcwd.return_value = '/tmp'
    main = mech.utils.main_dir()
    mock_os_getcwd.assert_called()
    assert main == '/tmp'


@patch('os.getcwd')
def test_mech_dir(mock_os_getcwd):
    mock_os_getcwd.return_value = '/tmp'
    mechdir = mech.utils.mech_dir()
    mock_os_getcwd.assert_called()
    assert mechdir == '/tmp/.mech'


def test_save_mechfile_empty_config():
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    m = mock_open()
    with patch('builtins.open', m, create=True):
        assert mech.utils.save_mechfile({})
    m.assert_called_once_with(filename, 'w+')
    m.return_value.write.assert_called_once_with('{}')


# TODO: Is there a better way to get data written?
def _get_data_written(m):
    written = ''
    for call in m.mock_calls:
        tmp = '{}'.format(call)
        if tmp.startswith('call().write('):
            line = tmp.replace("call().write('", '')
            line = line.replace("')", '')
            line = line.replace("\\n", '\n')
            written += line
    return written


def test_save_mechfile_one():
    first_dict = {
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
        }
    }
    first_json = '''{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  }
}'''  # noqa: 501
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    m = mock_open()
    with patch('builtins.open', m, create=True):
        assert mech.utils.save_mechfile(first_dict)
    m.assert_called_once_with(filename, 'w+')
    assert first_json == _get_data_written(m)


def test_save_mechfile_two():
    two_dict = {
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
    two_json = '''{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  },
  "second": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "second",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  }
}'''  # noqa: 501
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    m = mock_open()
    with patch('builtins.open', m, create=True):
        assert mech.utils.save_mechfile(two_dict)
    m.assert_called_once_with(filename, 'w+')
    assert two_json == _get_data_written(m)


def test_tar_cmd():
    """Note: not really a unit test per se, as it calls out."""
    assert ["tar"] == mech.utils.tar_cmd()


def test_config_ssh_string_empty():
    ssh_string = mech.utils.config_ssh_string({})
    assert ssh_string == "Host \n"


def test_config_ssh_string_simple():
    config = {
        "Host": "first",
        "User": "foo",
        "Port": "22",
        "UserKnownHostsFile": "/dev/null",
        "StrictHostKeyChecking": "no",
        "PasswordAuthentication": "no",
        "IdentityFile": 'blah',
        "IdentitiesOnly": "yes",
        "LogLevel": "FATAL",
    }
    ssh_string = mech.utils.config_ssh_string(config)
    assert ssh_string == 'Host first\n  User foo\n  Port 22\n  UserKnownHostsFile /dev/null\n  StrictHostKeyChecking no\n  PasswordAuthentication no\n  IdentityFile blah\n  IdentitiesOnly yes\n  LogLevel FATAL\n'  # noqa: E501


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_blank_name(load_mock, save_mock):
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, '', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_name_as_None(load_mock, save_mock):
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, None, True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_twice(load_mock, save_mock):
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()
    assert mech.utils.save_mechfile_entry(entry, 'first', True)


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={'first': {'name': 'first'}})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry(load_mock, save_mock):
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


def test_parse_vmx():
    partial_vmx = '''.encoding = "UTF-8"
bios.bootorder  = "hdd,cdrom"
checkpoint.vmstate     = ""

cleanshutdown = "FALSE"
config.version = "8"'''
    expected_vmx = OrderedDict([
        ('.encoding', '"UTF-8"'),
        ('bios.bootorder', '"hdd,cdrom"'),
        ('checkpoint.vmstate', '""'),
        ('cleanshutdown', '"FALSE"'),
        ('config.version', '"8"')
    ])
    m = mock_open(read_data=partial_vmx)
    with patch('builtins.open', m):
        assert mech.utils.parse_vmx(partial_vmx) == expected_vmx
    m.assert_called()
