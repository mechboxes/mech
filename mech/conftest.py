"""Common pytest code."""
import json
import pytest


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
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '--name': None,
        '--box': None,
        '<location>': None,
    }


@pytest.fixture
def mech_box_arguments():
    """Return the default 'mech box' arguments."""
    return {
        '--force': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '<location>': None,
    }


@pytest.fixture
def mech_init_arguments():
    """Return the default 'mech init' arguments."""
    return {
        '--force': False,
        '--insecure': False,
        '--cacert': None,
        '--capath': None,
        '--cert': None,
        '--box-version': None,
        '--checksum': None,
        '--checksum-type': None,
        '--name': None,
        '--box': None,
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


@pytest.fixture
def helpers():
    return Helpers
