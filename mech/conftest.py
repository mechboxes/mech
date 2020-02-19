# Copyright (c) 2020 Mike Kinney

"""Common pytest code."""
import json
import os
import pytest
import subprocess


from shutil import rmtree


@pytest.fixture
def mechfile_one_entry():
    """Return one mechfile entry."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0'
        }
    }


@pytest.fixture
def mechfile_one_entry_with_auth():
    """Return one mechfile entry with auth."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'auth': {
                'username': 'bob',
                'pub_key': 'some_pub_key_data'
            }
        }
    }


@pytest.fixture
def mechfile_two_entries():
    """Return two mechfile entries."""
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'shared_folders': [
                {
                    "host_path": ".",
                    "share_name": "mech"
                }
            ],
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        },
        'second': {
            'name': 'second',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
            'url':
            'https://vagrantcloud.com/bento/boxes/ubuntu-18.04/'
            'versions/201912.04.0/providers/vmware_desktop.box'
        }
    }


CATALOG = """{
    "description": "foo",
    "short_description": "foo",
    "name": "bento/ubuntu-18.04",
    "versions": [
        {
            "version": "aaa",
            "status": "active",
            "description_html": "foo",
            "description_markdown": "foo",
            "providers": [
                {
                    "name": "vmware_desktop",
                    "url": "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/\
versions/aaa/providers/vmware_desktop.box",
                    "checksum": null,
                    "checksum_type": null
                }
            ]
        }
    ]
}"""
@pytest.fixture
def catalog():
    """Return a catalog."""
    return CATALOG


@pytest.fixture
def catalog_as_json():
    """Return a catalog as json."""
    return json.loads(CATALOG)


@pytest.fixture
def mech_add_arguments():
    """Return the default 'mech add' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '--name': None,
        '--box': None,
        '--add-me': None,
        '--use-me': None,
        '<location>': None,
    }


@pytest.fixture
def mech_box_arguments():
    """Return the default 'mech box' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '<location>': None,
    }


@pytest.fixture
def mech_init_arguments():
    """Return the default 'mech init' arguments."""
    return {
        '--force': False,
        '--box-version': None,
        '--name': None,
        '--box': None,
        '--add-me': None,
        '--use-me': None,
        '<location>': None,
    }


class Helpers:
    @staticmethod
    def get_mock_data_written(a_mock):
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

    @staticmethod
    def kill_pids(pids):
        """Kill all pids."""
        for pid in pids:
            results = subprocess.run(args='kill {}'.format(pid), shell=True, capture_output=True)
            if results.returncode != 0:
                print("Could not kill pid:{}".format(pid))

    @staticmethod
    def find_vmx_for_dir(part_of_dir):
        """Return all pids that that are VMware VMs where
           the .vmx part_of_dir matches the full path."""
        pids = []
        results = subprocess.run(args='ps -ef | grep vmware-vmx | grep {} | grep -v grep'
                                 .format(part_of_dir), shell=True, capture_output=True)
        if results.returncode == 0:
            # we found a proc
            stdout = results.stdout.decode('utf-8')
            for line in stdout.split('\n'):
                data = line.split()
                if len(data) > 2:
                    # add pid to the collection
                    pids.append(data[1])
        return pids

    @staticmethod
    def cleanup_dir_and_vms_from_dir(a_dir):
        """Kill any vms from this directory, remove directory and re-create the directory."""
        Helpers.kill_pids(Helpers.find_vmx_for_dir(a_dir + '/.mech/'))
        rmtree(a_dir, ignore_errors=True)
        os.mkdir(a_dir)


@pytest.fixture
def helpers():
    """Helper functions for testing."""
    return Helpers
