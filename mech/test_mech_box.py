# Copyright (c) 2020 Mike Kinney

"""Unit tests for 'mech box'."""
import re

from unittest.mock import patch

import mech.command
import mech.mech
import mech.vmrun


@patch('os.getcwd')
def test_mech_box_list_no_mechdir(mock_os_getcwd, capfd):
    """Test 'mech box list' with no '.mech' directory."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechBox(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('./tmp', [], []), ]
        a_mech.list({})
        mock_walk.assert_called()
        out, _ = capfd.readouterr()
        # ensure a header prints out
        assert re.search(r'BOX', out, re.MULTILINE)


@patch('os.getcwd')
def test_mech_box_list_empty_boxes_dir(mock_os_getcwd, capfd):
    """Test 'mech box list' with no directories in '.mech/boxes' directory."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechBox(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('/tmp', ['boxes', ], []), ]
        a_mech.list({})
        mock_walk.assert_called()
        out, _ = capfd.readouterr()
        # ensure a header prints out
        assert re.search(r'BOX', out, re.MULTILINE)


@patch('os.getcwd')
def test_mech_box_list_one_box(mock_os_getcwd, capfd):
    """Test 'mech box list' with one box present."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechBox(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        # simulate: bento/ubuntu-18.04/201912.04.0/vmware_desktop.box
        mock_walk.return_value = [
            ('/tmp', ['boxes'], []),
            ('/tmp/boxes', ['bento'], []),
            ('/tmp/boxes/bento', ['ubuntu-18.04'], []),
            ('/tmp/boxes/bento/ubuntu-18.04', ['201912.04.0'], []),
            ('/tmp/boxes/bento/ubuntu-18.04/201912.04.0', [], ['vmware_desktop.box']),
        ]
        a_mech.list({})
        mock_walk.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'ubuntu-18.04', out, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_box_add_new(mock_os_getcwd, mock_os_path_exists,
                          mock_requests_get, capfd, catalog_as_json,
                          mech_box_arguments):
    """Test 'mech box add' from Hashicorp'."""
    mock_os_path_exists.return_value = False
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json

    a_mech = mech.mech.MechBox(arguments=global_arguments)
    arguments = mech_box_arguments
    arguments['<location>'] = 'bento/ubuntu-19.10'
    a_mech.add(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'Checking box', out, re.MULTILINE)


@patch('requests.get')
@patch('os.path.exists')
@patch('os.getcwd')
def test_mech_box_add_existing(mock_os_getcwd, mock_os_path_exists,
                               mock_requests_get, capfd, catalog_as_json,
                               mech_box_arguments):
    """Test 'mech box add' from Hashicorp'."""
    mock_os_getcwd.return_value = '/tmp'
    mock_os_path_exists.return_value = True
    global_arguments = {'--debug': False}
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = catalog_as_json

    a_mech = mech.mech.MechBox(arguments=global_arguments)
    arguments = mech_box_arguments
    arguments['<location>'] = 'bento/ubuntu-19.10'
    a_mech.add(arguments)
    out, _ = capfd.readouterr()
    assert re.search(r'Loading metadata', out, re.MULTILINE)


@patch('shutil.rmtree')
@patch('os.path.exists')
def test_mech_box_remove_exists(mock_os_path_exists, mock_rmtree, capfd):
    """Test 'mech box remove'."""
    mock_os_path_exists.return_value = True
    mock_rmtree.return_value = True
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechBox(arguments=global_arguments)
    arguments = {
        '<name>': 'bento/ubuntu-18.04',
        '<version>': 'somever',
    }
    a_mech.remove(arguments)
    out, _ = capfd.readouterr()
    mock_os_path_exists.assert_called()
    mock_rmtree.assert_called()
    assert re.search(r'Removed ', out, re.MULTILINE)


@patch('os.path.exists')
def test_mech_box_remove_does_not_exists(mock_os_path_exists, capfd):
    """Test 'mech box remove'."""
    mock_os_path_exists.return_value = False
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechBox(arguments=global_arguments)
    arguments = {
        '<name>': 'bento/ubuntu-18.04',
        '<version>': 'somever',
    }
    a_mech.remove(arguments)
    out, _ = capfd.readouterr()
    mock_os_path_exists.assert_called()
    assert re.search(r'No boxes were removed', out, re.MULTILINE)
