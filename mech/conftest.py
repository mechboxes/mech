"""Common pytest code."""
import pytest
import json


@pytest.fixture
def mechfile_one_entry():
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0'
        }
    }


@pytest.fixture
def mechfile_two_entries():
    return {
        'first': {
            'name': 'first',
            'box': 'bento/ubuntu-18.04',
            'box_version': '201912.04.0',
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


@pytest.fixture
def catalog_as_json():
    catalog = """{
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
    catalog_as_json = json.loads(catalog)
    return catalog_as_json


@pytest.fixture
def mech_add_arguments():
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
