"""Test the mech cli. """
import subprocess
import re


def test_version():
    rc, out = subprocess.getstatusoutput('mech --version')
    assert re.match(r'mech v[0-9]+\.[0-9]+\.[0-9]', out)
    assert rc == 0


def test_help():
    rc, out = subprocess.getstatusoutput('mech --help')
    assert re.match(r'Usage: mech ', out)
    assert rc == 0
