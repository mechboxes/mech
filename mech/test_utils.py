"""Test mech utils."""
import os

from unittest.mock import patch, mock_open
from collections import OrderedDict
from pytest import raises

import mech.utils


@patch('os.getcwd')
def test_main_dir(mock_os_getcwd):
    """Test main_dir()."""
    mock_os_getcwd.return_value = '/tmp'
    main = mech.utils.main_dir()
    mock_os_getcwd.assert_called()
    assert main == '/tmp'


@patch('os.getcwd')
def test_mech_dir(mock_os_getcwd):
    """Test mech_dir()."""
    mock_os_getcwd.return_value = '/tmp'
    mechdir = mech.utils.mech_dir()
    mock_os_getcwd.assert_called()
    assert mechdir == '/tmp/.mech'


def test_save_mechfile_empty_config():
    """Test save_mechfile with empty configuration."""
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile({})
    a_mock.assert_called_once_with(filename, 'w+')
    a_mock.return_value.write.assert_called_once_with('{}')


def _get_data_written(a_mock):
    """Helper function to get the data written to a mocked file."""
    written = ''
    for call in a_mock.mock_calls:
        tmp = '{}'.format(call)
        if tmp.startswith('call().write('):
            line = tmp.replace("call().write('", '')
            line = line.replace("')", '')
            line = line.replace("\\n", '\n')
            written += line
    return written


def test_save_mechfile_one():
    """Test save_mechfile with one entry."""
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
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile(first_dict)
    a_mock.assert_called_once_with(filename, 'w+')
    assert first_json == _get_data_written(a_mock)


def test_save_mechfile_two():
    """Test save_mechfile with two entries."""
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
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile(two_dict)
    a_mock.assert_called_once_with(filename, 'w+')
    assert two_json == _get_data_written(a_mock)


def test_tar_cmd():
    """Note: not really a unit test per se, as it calls out."""
    assert ["tar"] == mech.utils.tar_cmd()


def test_config_ssh_string_empty():
    """Test config_ssh_string with empty configuration."""
    ssh_string = mech.utils.config_ssh_string({})
    assert ssh_string == "Host \n"


def test_config_ssh_string_simple():
    """Test config_ssh_string with a simple configuration."""
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
    assert ssh_string == 'Host first\n  User foo\n  Port 22\n  UserKnownHostsFile /dev/null\n  StrictHostKeyChecking no\n  PasswordAuthentication no\n  IdentityFile blah\n  IdentitiesOnly yes\n  LogLevel FATAL\n'  # noqa: E501  pylint: disable=line-too-long


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    """Test save_mechfile_entry with no entries in the mechfile."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_blank_name(load_mock, save_mock):
    """Test save_mechfile_entry with a blank name."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, '', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_with_name_as_none(load_mock, save_mock):
    """Test save_mechfile_entry with name as None."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, None, True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_save_mechfile_entry_twice(load_mock, save_mock):
    """Test save_mechfile_entry multiple times."""
    entry = {'first': {'name': 'first'}}
    assert mech.utils.save_mechfile_entry(entry, 'first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()
    assert mech.utils.save_mechfile_entry(entry, 'first', True)


@patch('mech.utils.load_mechfile', return_value={})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry_with_empty_mechfile(load_mock, save_mock):
    """Test remove_mechfile_entry with no entries in the mechfile."""
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


@patch('mech.utils.load_mechfile', return_value={'first': {'name': 'first'}})
@patch('mech.utils.save_mechfile', return_value=True)
def test_remove_mechfile_entry(load_mock, save_mock):
    """Test remove_mechfile_entry."""
    assert mech.utils.remove_mechfile_entry('first', True)
    load_mock.assert_called_once()
    save_mock.assert_called_once()


def test_parse_vmx():
    """Test parse_vmx."""
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
    a_mock = mock_open(read_data=partial_vmx)
    with patch('builtins.open', a_mock):
        assert mech.utils.parse_vmx(partial_vmx) == expected_vmx
    a_mock.assert_called()


def test_build_mechfile_entry_no_location():
    """Test if None is used for location."""
    assert mech.utils.build_mechfile_entry(location=None) == {}


def test_build_mechfile_entry_https_location():
    """Test if location starts with 'https://'."""
    assert mech.utils.build_mechfile_entry(location='https://foo') == {
        'box': None,
        'box_version': None,
        'name': 'first',
        'url': 'https://foo'
    }


def test_build_mechfile_entry_http_location():
    """Test if location starts with 'http://'."""
    assert mech.utils.build_mechfile_entry(location='http://foo') == {
        'box': None,
        'box_version': None,
        'name': 'first',
        'url':
        'http://foo'
    }


def test_build_mechfile_entry_ftp_location():
    """Test if location starts with 'ftp://'."""
    assert mech.utils.build_mechfile_entry(location='ftp://foo') == {
        'box': None,
        'box_version': None,
        'name': 'first',
        'url': 'ftp://foo'
    }


def test_build_mechfile_entry_ftp_location_with_other_values():
    """Test if mechfile_entry is filled out."""
    expected = {
        'box': 'bbb',
        'box_version': 'ccc',
        'name': 'aaa',
        'url': 'ftp://foo'
    }
    assert mech.utils.build_mechfile_entry(location='ftp://foo', name='aaa',
                                           box='bbb', box_version='ccc') == expected


def test_build_mechfile_entry_file_location_json():
    """Test if location starts with 'file:' and contains valid json."""

    # Note: Download/format json like this:
    # curl --header 'Accept:application/json' \
    #    'https://app.vagrantup.com/bento/boxes/ubuntu-18.04' | python3 -m json.tool
    json_data = """{
        "description": "foo",
        "short_description": "foo",
        "name": "bento/ubuntu-18.04",
        "versions": [
            {
                "version": "202002.04.0",
                "status": "active",
                "description_html": "foo",
                "description_markdown": "foo",
                "providers": [
                    {
                        "name": "vmware_desktop",
                        "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/202002.04.0/providers/vmware_desktop.box",
                        "checksum": null,
                        "checksum_type": null
                    }
                ]
            }
        ]
    }"""
    expected = {
        'box': 'bento/ubuntu-18.04',
        'box_version': '202002.04.0',
        'name': 'first',
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/202002.04.0/providers/vmware_desktop.box'
    }
    a_mock = mock_open(read_data=json_data)
    with patch('builtins.open', a_mock):
        actual = mech.utils.build_mechfile_entry(location='file:/tmp/one.json')
        assert expected == actual
    a_mock.assert_called()


def test_build_mechfile_entry_file_location_but_file_not_found():
    """Test if location starts with 'file:' and file does not exist."""
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = SystemExit()
        with raises(SystemExit):
            mech.utils.build_mechfile_entry(location='file:/tmp/one.box')
