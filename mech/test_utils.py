import os

from unittest.mock import patch, mock_open

import mech.utils


def test_main_dir():
    main = mech.utils.main_dir()
    assert main.startswith('/')


def test_mech_dir():
    mech_dir = mech.utils.mech_dir()
    assert mech_dir.startswith('/')
    assert mech_dir.endswith('/.mech')


def test_save_mechfile_empty_config():
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    m = mock_open()
    with patch('builtins.open', m, create=True):
        assert mech.utils.save_mechfile({})
    m.assert_called_once_with(filename, 'w+')
    m.return_value.write.assert_called_once_with('{}')


def test_save_mechfile_simple_config():
    first_dict = {'first': {
        'name': 'first',
        'box': 'bento/ubuntu-18.04',
        'box_version': '201912.04.0',
        'url': 'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box'
      }
    }
    first_json = '''{
  "first": {
    "box": "bento/ubuntu-18.04",
    "box_version": "201912.04.0",
    "name": "first",
    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/201912.04.0/providers/vmware_desktop.box"
  }
}'''
    filename = os.path.join(mech.utils.main_dir(), 'Mechfile')
    m = mock_open()
    with patch('builtins.open', m, create=True):
        assert mech.utils.save_mechfile(first_dict)
    m.assert_called_once_with(filename, 'w+')

    # print('calls to the file:\n', m.mock_calls, end ='\n\n')

    # TODO: Is there a better way to get data written?
    written = ''
    for call in m.mock_calls:
        tmp = '{}'.format(call)
        if tmp.startswith('call().write('):
            line = tmp.replace("call().write('", '')
            line = line.replace("')", '')
            line = line.replace("\\n", '\n')
            written += line
    assert written == first_json


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
    assert ssh_string == 'Host first\n  User foo\n  Port 22\n  UserKnownHostsFile /dev/null\n  StrictHostKeyChecking no\n  PasswordAuthentication no\n  IdentityFile blah\n  IdentitiesOnly yes\n  LogLevel FATAL\n'
