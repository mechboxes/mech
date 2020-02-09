"""Unit tests for 'mech snapshot'."""
import re

from unittest.mock import patch

import mech.command
import mech.mech
import mech.vmrun


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
@patch('os.getcwd')
def test_mech_snapshot_list_no_mechdir(mock_os_getcwd, mock_load_mechfile, capfd):
    """Test 'mech snapshot list' with no '.mech' directory."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechSnapshot(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        # root, dirs, files
        mock_walk.return_value = [('./tmp', [], []), ]
        arguments = {'<instance>': None}
        a_mech.list(arguments)
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        out, _ = capfd.readouterr()
        # ensure a header prints out
        assert re.search(r'Snapshots', out, re.MULTILINE)


SNAPSHOT_LIST_WITHOUT_SNAPSHOTS = """Snapshots for instance:first
Total snapshots: 0
Snapshots for instance:second
Instance (second) is not created."""
@patch('mech.vmrun.VMrun.list_snapshots', return_value=SNAPSHOT_LIST_WITHOUT_SNAPSHOTS)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('os.getcwd')
def test_mech_snapshot_list_no_snapshots(mock_os_getcwd, mock_load_mechfile,
                                         mock_list_snapshots, capfd):
    """Test 'mech snapshot list' without any snapshots."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechSnapshot(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/tmp', ['first'], []),
            ('/tmp/first', [], ['some.vmx']),
        ]

        # with no args
        arguments = {'<instance>': None}
        a_mech.list(arguments)
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'Total snapshots: 0', out, re.MULTILINE)
        assert re.search(r'Instance \(second\) is not created.', out, re.MULTILINE)

        # single instance
        arguments = {'<instance>': 'first'}
        a_mech.list(arguments)
        out, _ = capfd.readouterr()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 0', out, re.MULTILINE)


SNAPSHOT_LIST_WITH_SNAPSHOT = """Snapshots for instance:first
Total snapshots: 1
foo
Snapshots for instance:second
Instance (second) is not created."""
@patch('mech.vmrun.VMrun.list_snapshots', return_value=SNAPSHOT_LIST_WITH_SNAPSHOT)
@patch('mech.utils.load_mechfile', return_value=MECHFILE_TWO_ENTRIES)
@patch('os.getcwd')
def test_mech_snapshot_list_with_snapshot(mock_os_getcwd, mock_load_mechfile,
                                          mock_list_snapshots, capfd):
    """Test 'mech snapshot list' with a snapshots."""
    mock_os_getcwd.return_value = '/tmp'
    global_arguments = {'--debug': False}
    a_mech = mech.mech.MechSnapshot(arguments=global_arguments)
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/tmp', ['first'], []),
            ('/tmp/first', [], ['some.vmx']),
        ]

        # with no args
        arguments = {'<instance>': None}
        a_mech.list(arguments)
        mock_walk.assert_called()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        out, _ = capfd.readouterr()
        assert re.search(r'Total snapshots: 1', out, re.MULTILINE)
        assert re.search(r'Instance \(second\) is not created.', out, re.MULTILINE)

        # single instance
        arguments = {'<instance>': 'first'}
        a_mech.list(arguments)
        out, _ = capfd.readouterr()
        mock_load_mechfile.assert_called()
        mock_list_snapshots.assert_called()
        assert re.search(r'Total snapshots: 1', out, re.MULTILINE)
