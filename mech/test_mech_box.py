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
    """Test 'mech box list' with no directories in '.mech/boxes' driectory."""
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
