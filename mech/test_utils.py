# Copyright (c) 2020 Mike Kinney

"""Test mech utils."""
import os
import re

from unittest.mock import patch, mock_open, MagicMock
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


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile(mock_os_getcwd, mock_os_path_isfile, mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = True
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.load_mechfile() == expected
    a_mock.assert_called()
    mock_os_getcwd.assert_called()


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_no_mechfile(mock_os_getcwd, mock_os_path_isfile, mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = False
    with raises(SystemExit):
        a_mock = mock_open()
        with patch('builtins.open', a_mock, create=True):
            mech.utils.load_mechfile()


@patch('json.loads')
@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_no_mechfile_should_not_exist(mock_os_getcwd, mock_os_path_isfile,
                                                    mock_json_loads):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    mock_json_loads.return_value = expected
    mock_os_path_isfile.return_value = False
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        got = mech.utils.load_mechfile(should_exist=False)
    assert got == expected
    mock_os_getcwd.assert_called()


@patch('os.path.isfile')
@patch('os.getcwd')
def test_load_mechfile_invalid_json(mock_os_getcwd, mock_os_path_isfile):
    """Test mech_load_mechfile()."""
    mock_os_getcwd.return_value = '/tmp'
    expected = {}
    # bad_json below is missing a comma between elements
    bad_json = '''{"foo": "bar" "foo2": 1}'''
    mock_os_path_isfile.return_value = True
    a_mock = mock_open(read_data=bad_json)
    with patch('builtins.open', a_mock, create=True):
        got = mech.utils.load_mechfile()
    assert got == expected
    a_mock.assert_called()
    mock_os_getcwd.assert_called()


def test_save_mechfile_empty_config():
    """Test save_mechfile with empty configuration."""
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        assert mech.utils.save_mechfile({})
    a_mock.assert_called_once_with(filename, 'w+')
    a_mock.return_value.write.assert_called_once_with('{}')


def test_save_mechfile_one(helpers):
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
    assert first_json == helpers.get_mock_data_written(a_mock)


def test_save_mechfile_two(helpers):
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
    assert two_json == helpers.get_mock_data_written(a_mock)


def test_tar_cmd():
    """Test tar cmd.
       Note: not really a unit test per se, as it calls out.
    """
    assert ["tar"] == mech.utils.tar_cmd()


def test_tar_cmd_when_tar_not_found():
    """Test tar cmd."""
    a_mock = MagicMock()
    a_mock.return_value = None
    a_mock.returncode = None
    a_mock.side_effect = OSError()
    with patch('subprocess.Popen', a_mock):
        tar = mech.utils.tar_cmd()
        assert tar is None


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


@patch('mech.utils.parse_vmx')
def test_update_vmx_empty(mock_parse_vmx, helpers, capfd):
    """Test update_vmx."""
    expected_vmx = """ethernet0.addresstype = generated
ethernet0.bsdname = en0
ethernet0.connectiontype = nat
ethernet0.displayname = Ethernet
ethernet0.linkstatepropagation.enable = FALSE
ethernet0.pcislotnumber = 32
ethernet0.present = TRUE
ethernet0.virtualdev = e1000
ethernet0.wakeonpcktrcv = FALSE
"""
    mock_parse_vmx.return_value = {}
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx')
        a_mock.assert_called()
        got = helpers.get_mock_data_written(a_mock)
        assert expected_vmx == got
        out, _ = capfd.readouterr()
        assert re.search(r'Added network interface to vmx file', out, re.MULTILINE)


@patch('mech.utils.parse_vmx')
def test_update_vmx_with_a_network_entry(mock_parse_vmx, capfd):
    """Test update_vmx."""
    mock_parse_vmx.return_value = {'ethernet0.present': 'true'}
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx')
        assert not a_mock.called, 'should not have written anything to the vmx file'
        out, _ = capfd.readouterr()
        assert out == ''


@patch('mech.utils.parse_vmx')
def test_update_vmx_with_cpu_and_memory(mock_parse_vmx, helpers, capfd):
    """Test update_vmx."""
    mock_parse_vmx.return_value = {'ethernet0.present': 'true'}
    expected_vmx = '''ethernet0.present = true
numvcpus = "3"
memsize = "1025"
'''
    a_mock = mock_open()
    with patch('builtins.open', a_mock, create=True):
        mech.utils.update_vmx('/tmp/first/one.vmx', numvcpus=3, memsize=1025)
        a_mock.assert_called()
        got = helpers.get_mock_data_written(a_mock)
        assert expected_vmx == got
        out, _ = capfd.readouterr()
        assert out == ''


def test_build_mechfile_entry_no_location():
    """Test if None is used for location."""
    assert mech.utils.build_mechfile_entry(location=None) == {}


def test_build_mechfile_entry_https_location():
    """Test if location starts with 'https://'."""
    assert mech.utils.build_mechfile_entry(location='https://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url': 'https://foo'
    }


def test_build_mechfile_entry_http_location():
    """Test if location starts with 'http://'."""
    assert mech.utils.build_mechfile_entry(location='http://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url':
        'http://foo'
    }


def test_build_mechfile_entry_ftp_location():
    """Test if location starts with 'ftp://'."""
    assert mech.utils.build_mechfile_entry(location='ftp://foo') == {
        'box': None,
        'box_version': None,
        'name': None,
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url': 'ftp://foo'
    }


def test_build_mechfile_entry_ftp_location_with_other_values():
    """Test if mechfile_entry is filled out."""
    expected = {
        'box': 'bbb',
        'box_version': 'ccc',
        'name': 'aaa',
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url': 'ftp://foo'
    }
    assert mech.utils.build_mechfile_entry(location='ftp://foo', name='aaa',
                                           box='bbb', box_version='ccc') == expected


def test_build_mechfile_entry_file_location_json(catalog):
    """Test if location starts with 'file:' and contains valid json."""

    # Note: Download/format json like this:
    # curl --header 'Accept:application/json' \
    #    'https://app.vagrantup.com/bento/boxes/ubuntu-18.04' | python3 -m json.tool
    expected = {
        'box': 'bento/ubuntu-18.04',
        'box_version': 'aaa',
        'name': 'first',
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box'
    }
    a_mock = mock_open(read_data=catalog)
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


@patch('requests.get')
def test_build_mechfile_entry_file_location_external_good(mock_requests_get,
                                                          catalog_as_json):
    """Test if location talks to Hashicorp."""
    expected = {
        'box': 'bento/ubuntu-18.04',
        'box_version': 'aaa',
        'name': None,
        'shared_folders': [{'host_path': '../..', 'share_name': 'mech'}],
        'url':
        'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box'
    }
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    actual = mech.utils.build_mechfile_entry(location='bento/ubuntu-18.04')
    mock_requests_get.assert_called()
    assert expected == actual


def test_build_mechfile_entry_file_location_external_bad_location():
    """Test if we do not have a valid location. (must be in form of 'hashiaccount/boxname')."""
    with raises(SystemExit, match=r"Provided box name is not valid"):
        mech.utils.build_mechfile_entry(location='bento')


def test_provision_no_instance():
    """Test provisioning."""
    with raises(SystemExit, match=r"Need to provide an instance to provision"):
        mech.utils.provision(instance=None, show=None)


def test_provision_no_vmx():
    """Test provisioning."""
    mock_inst = MagicMock()
    mock_inst.vmx = None
    with raises(SystemExit, match=r"Need to provide vmx.*"):
        mech.utils.provision(instance=mock_inst, show=None)


@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_no_vmare_tools(mock_installed_tools):
    """Test provisioning."""
    mock_inst = MagicMock()
    mock_installed_tools.return_value = None
    with raises(SystemExit, match=r"Cannot provision if VMware Tools are not installed"):
        mech.utils.provision(instance=mock_inst, show=None)


@patch('mech.utils.provision_file')
@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_file_no_provisioning(mock_installed_tools, mock_provision_file, capfd):
    """Test provisioning."""
    mock_installed_tools.return_value = "running"
    mock_provision_file.return_value = None
    mock_inst = MagicMock()
    mock_inst.provision = []
    mock_inst.created = True
    mock_inst.use_psk = False
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    assert re.search(r'Nothing to provision', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.copy_file_from_host_to_guest')
@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_file(mock_installed_tools, mock_copy_file, capfd):
    """Test provisioning."""
    mock_installed_tools.return_value = "running"
    mock_copy_file.return_value = True
    config = [
        {
            "type": "file",
            "source": "file1.txt",
            "destination": "/tmp/file1.txt",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mock_inst.use_psk = False
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    assert re.search(r'Copying ', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.copy_file_from_host_to_guest')
@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_file_could_not_copy_file_to_guest(mock_installed_tools,
                                                     mock_copy_file, capfd):
    """Test provisioning."""
    mock_installed_tools.return_value = "running"
    mock_copy_file.return_value = None
    config = [
        {
            "type": "file",
            "source": "file1.txt",
            "destination": "/tmp/file1.txt",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mock_inst.use_psk = False
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools')
def test_provision_file_show(mock_installed_tools, capfd):
    """Test provisioning."""
    mock_installed_tools.return_value = "running"
    config = [
        {
            "type": "file",
            "source": "file1.txt",
            "destination": "/tmp/file1.txt",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=True)
    out, _ = capfd.readouterr()
    assert re.search(r'instance:', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.delete_file_in_guest', return_value=True)
@patch('mech.vmrun.VMrun.run_program_in_guest', return_value=True)
@patch('mech.vmrun.VMrun.run_script_in_guest', return_value=True)
@patch('os.path.isfile', return_value=True)
@patch('mech.vmrun.VMrun.create_tempfile_in_guest', return_value='/tmp/foo')
@patch('mech.vmrun.VMrun.copy_file_from_host_to_guest', return_value=True)
@patch('mech.vmrun.VMrun.installed_tools', return_value="running")
def test_provision_shell(mock_installed_tools, mock_copy_file,
                         mock_create_tempfile, mock_isfile,
                         mock_run_script_in_guest, mock_run_program_in_guest,
                         mock_delete_file_in_guest, capfd):
    """Test provisioning."""
    config = [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
        {
            "type": "shell",
            "inline": "echo hello from inline"
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mock_inst.use_psk = False
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    mock_installed_tools.assert_called()
    mock_copy_file.assert_called()
    mock_create_tempfile.assert_called()
    mock_isfile.assert_called()
    mock_run_script_in_guest.assert_called()
    mock_run_program_in_guest.assert_called()
    mock_delete_file_in_guest.assert_called()
    assert re.search(r'Configuring script', out, re.MULTILINE)
    assert re.search(r'Configuring environment', out, re.MULTILINE)
    assert re.search(r'Configuring script to run inline', out, re.MULTILINE)
    assert re.search(r'Executing program', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools', return_value="running")
def test_provision_shell_show_only(mock_installed_tools, capfd):
    """Test provisioning."""
    config = [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=True)
    out, _ = capfd.readouterr()
    mock_installed_tools.assert_called()
    assert re.search(r' instance:', out, re.MULTILINE)


@patch('mech.utils.provision_shell', return_value=None)
@patch('mech.vmrun.VMrun.installed_tools', return_value="running")
def test_provision_shell_with_issue(mock_installed_tools, mock_provision_shell,
                                    capfd):
    """Test provisioning."""
    config = [
        {
            "type": "shell",
            "path": "file1.sh",
            "args": [
                "a=1",
                "b=true",
            ],
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    mock_installed_tools.assert_called()
    mock_provision_shell.assert_called()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


@patch('mech.vmrun.VMrun.installed_tools', return_value="running")
def test_provision_with_unknown_type(mock_installed_tools, capfd):
    """Test provisioning."""
    config = [
        {
            "type": "foo",
        },
    ]
    mock_inst = MagicMock()
    mock_inst.name = 'first'
    mock_inst.vmx = '/tmp/first/some.vmx'
    mock_inst.provision = config
    mech.utils.provision(instance=mock_inst, show=None)
    out, _ = capfd.readouterr()
    mock_installed_tools.assert_called()
    assert re.search(r'Not Provisioned', out, re.MULTILINE)


@patch('os.environ')
def test_get_fallback_executable_no_path_in_environ(mock_os_environ):
    """Weird case where PATH is is not in the environment."""
    mock_os_environ.return_value = ''
    assert mech.utils.get_fallback_executable() is None


@patch('os.path.exists')
def test_get_fallback_executable(mock_os_path_exists):
    """Find vmrun in PATH."""
    mock_os_path_exists.return_value = True
    with patch.dict('os.environ', {'PATH': '/tmp:/tmp2'}):
        got = mech.utils.get_fallback_executable()
    expected = '/tmp/vmrun'
    assert got == expected
    mock_os_path_exists.assert_called()


@patch('os.path.exists')
def test_darwin_executable_when_installed(mock_os_path_exists):
    """Find vmrun in PATH."""
    expected = '/Applications/VMware Fusion.app/Contents/Library/vmrun'
    mock_os_path_exists.return_value = True
    got = mech.utils.get_darwin_executable()
    assert expected == got
    mock_os_path_exists.assert_called()


@patch('os.path.exists')
def test_darwin_executable_when_not_installed(mock_os_path_exists):
    """Find vmrun in PATH."""
    # deal with a different file returns a different mocked value
    def side_effect(filename):
        if filename == '/Applications/VMware Fusion.app/Contents/Library/vmrun':
            return False
        else:
            return True
    mock_os_path_exists.side_effect = side_effect
    expected = '/tmp/vmrun'
    with patch.dict('os.environ', {'PATH': '/tmp:/tmp2'}):
        got = mech.utils.get_darwin_executable()
    assert expected == got


def test_catalog_to_mechfile_when_empty_catalog():
    """Test catalog_to_mechfile."""
    catalog = {}
    with raises(SystemExit):
        mech.utils.catalog_to_mechfile(catalog)


@patch('mech.utils.locate')
def test_init_box_cannot_find_valid_box(mock_locate):
    """Test init_box."""
    mock_locate.return_value = None
    with raises(SystemExit):
        mech.utils.init_box(name='first')


def test_add_mechfile_with_empty_mechfile():
    """Test add_mechfile."""
    mech.utils.add_mechfile(mechfile_entry={})


@patch('requests.get')
@patch('mech.utils.locate')
def test_add_box_url(mock_locate, mock_requests_get, catalog_as_json):
    """Test init_box."""
    mock_locate.return_value = False
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json
    got = mech.utils.add_box_url(name='first', box='abox', box_version='aver', url='')
    assert got is None


@patch('os.getlogin', return_value='bob')
@patch('os.path.expanduser', return_value='/home/bob/id_rsa.pub')
def test_get_info_for_auth(mock_path_expanduser, mock_getlogin):
    """Test get_info_for_auth."""
    expected = {'auth': {'username': 'bob', 'pub_key': '/home/bob/id_rsa.pub', 'mech_use': False}}
    got = mech.utils.get_info_for_auth()
    assert got == expected
