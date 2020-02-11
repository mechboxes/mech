"""Common pytest code."""

import pytest


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
