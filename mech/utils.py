# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from __future__ import division

import os
import re
import sys
import json
import tarfile
import fnmatch
import logging
import tempfile
import textwrap
import subprocess
import collections
from shutil import copyfile

import requests

from clint.textui import colored, puts_err
from clint.textui import progress


logger = logging.getLogger(__name__)


HOME = os.path.expanduser('~/.mech')


def confirm(prompt, default='y'):
    default = default.lower()
    if default not in ['y', 'n']:
        default = 'y'
    choicebox = '[Y/n]' if default == 'y' else '[y/N]'
    prompt = prompt + ' ' + choicebox + ' '

    while True:
        input = raw_input(prompt).strip()
        if input == '':
            if default == 'y':
                return True
            else:
                return False

        if re.match('y(?:es)?', input, re.IGNORECASE):
            return True

        elif re.match('n(?:o)?', input, re.IGNORECASE):
            return False


def save_mechfile(mechfile, directory='.'):
    puts_err(colored.blue("Saving {}".format(os.path.join(directory, 'mechfile'))))
    with open(os.path.join(directory, 'mechfile'), 'w+') as f:
        json.dump(mechfile, f, sort_keys=True, indent=4, separators=(',', ': '))
    puts_err(colored.green("Finished."))


def locate(path, glob):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, glob):
                return os.path.abspath(os.path.join(root, filename))


def parse_vmx(path):
    vmx = collections.OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip().split('=', 1)
            vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def update_vmx(path):
    vmx = parse_vmx(path)

    # Check if there is an existing interface
    for vmx_key in vmx:
        if vmx_key.startswith('ethernet'):
            return False

    # Write one if there is not
    vmx["ethernet0.addresstype"] = "generated"
    vmx["ethernet0.bsdname"] = "en0"
    vmx["ethernet0.connectiontype"] = "nat"
    vmx["ethernet0.displayname"] = "Ethernet"
    vmx["ethernet0.linkstatepropagation.enable"] = "FALSE"
    vmx["ethernet0.pcislotnumber"] = "32"
    vmx["ethernet0.present"] = "TRUE"
    vmx["ethernet0.virtualdev"] = "e1000"
    vmx["ethernet0.wakeonpcktrcv"] = "FALSE"

    with open(path, 'w') as new_vmx:
        for key in vmx:
            value = vmx[key]
            row = "{} = {}".format(key, value)
            new_vmx.write(row + os.linesep)

    return True


def load_mechfile():
    pwd = os.getcwd()
    while pwd:
        mechfile = os.path.join(pwd, 'mechfile')
        if os.path.isfile(mechfile):
            with open(mechfile) as f:
                try:
                    return json.load(f)
                except ValueError:
                    puts_err(colored.red("Invalid mechfile.\n"))
                    break
        new_pwd = os.path.basename(pwd)
        pwd = None if new_pwd == pwd else new_pwd
    puts_err(colored.red(textwrap.fill(
        "Couldn't find a mechfile in the current directory any deeper directories"
        "You can specify the name of the VM you'd like to start with mech up <name>"
        "Or run mech init to setup a tarball of your VM or download the VM"
    )))
    sys.exit(1)


def add_box(descriptor, name=None, version=None, force=False, requests_kwargs={}):
    if name is None:
        name = os.path.splitext(os.path.basename(descriptor))[0]

    if any(descriptor.startswith(s) for s in ('https://', 'http://', 'ftp://')):
        return add_box_url(name, version, descriptor, force=force, requests_kwargs=requests_kwargs)
    elif os.path.isfile(descriptor):
        try:
            with open(descriptor) as f:
                catalog = json.load(f)
        except Exception:
            return add_box_tar(name, version, descriptor, force=force)
    else:
        try:
            account, box, v = (descriptor.split('/', 2) + ['', ''])[:3]
            if v:
                version = v
            url = 'https://app.vagrantup.com/{}/boxes/{}'.format(account, box)
            catalog = requests.get(url, **requests_kwargs).json()
        except requests.ConnectionError:
            puts_err(colored.red("Couldn't connect to HashiCorp's Vagrant Cloud API"))
            return

    versions = catalog.get('versions', [])
    for v in versions:
        current_version = v['version']
        if not version or current_version == version:
            for provider in v['providers']:
                if 'vmware' in provider['name']:
                    url = provider['url']
                    puts_err(colored.blue("Found url {} with provider {}".format(url, provider['name'])))
                    return add_box_url(name, current_version, url, force=force, requests_kwargs=requests_kwargs)
    puts_err(colored.red("Couldn't find a VMWare compatible VM"))


def add_box_url(name, version, url, force=False, requests_kwargs={}):
    boxname = os.path.basename(url)
    box = os.path.join(*filter(None, (HOME, 'boxes', name, version, boxname)))
    exists = os.path.exists(box)
    if not exists or force:
        if exists:
            puts_err(colored.blue("Attempting to download box '{}'...".format(name)))
        else:
            puts_err(colored.blue("Box '{}' could not be found. Attempting to download...".format(name)))
        try:
            r = requests.get(url, stream=True, **requests_kwargs)
            length = int(r.headers['content-length'])
            with tempfile.NamedTemporaryFile() as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), label=boxname, expected_size=(length // 1024) + 1):
                    if chunk:
                        f.write(chunk)
                f.flush()
                add_box_tar(name, version, f.name, url=url, force=force)
        except requests.ConnectionError:
            puts_err(colored.red("Couldn't connect to %s" % url))
            return
    return name, version


def add_box_tar(name, version, filename, url=None, force=False):
    puts_err(colored.blue("Checking box '{}' integrity...".format(name)))

    if os.name == 'posix':
        proc = subprocess.Popen(['tar', '-tqf' if sys.platform.startswith('darwin') else '-tf', filename, '*.vmx'])
        valid_tar = not proc.wait()
    else:
        tar = tarfile.open(filename, 'r')
        files = tar.getnames()
        valid_tar = False
        for i in files:
            if i.endswith('vmx'):
                valid_tar = True
                break
            if i.startswith('/') or i.startswith('..'):
                puts_err(colored.red(textwrap.fill(
                    "This box is comprised of filenames starting with '/' or '..'"
                    "Exiting for the safety of your files"
                )))
                sys.exit(1)

    if valid_tar:
        boxname = os.path.basename(url if url else filename)
        box = os.path.join(*filter(None, (HOME, 'boxes', name, version, boxname)))
        path = os.path.dirname(box)
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(box) or force:
            copyfile(filename, box)
        return name, version


def init_mechfile(name, version):
    save_mechfile({
        'box': name,
        'box_version': version,
    }, '.')


def get_requests_kwargs(arguments):
    requests_kwargs = {}
    if arguments['--insecure']:
        requests_kwargs['verify'] = False
    elif arguments['--capath']:
        requests_kwargs['verify'] = arguments['--capath']
    elif arguments['--cacert']:
        requests_kwargs['verify'] = arguments['--cacert']
    elif arguments['--cert']:
        requests_kwargs['cert'] = arguments['--cert']
    return requests_kwargs


def get_vmx():
    vmx = locate('.mech', '*.vmx')
    if not vmx:
        puts_err(colored.red("Cannot locate a VMX file"))
        sys.exit(1)

    if update_vmx(vmx):
        puts_err(colored.yellow("Added network interface to vmx file"))

    return vmx


def init_box(name, version, requests_kwargs={}):
    if not os.path.exists('.mech'):
        name_version = add_box(name, name=name, version=version, requests_kwargs=requests_kwargs)
        if not name_version:
            return
        name, version = name_version
        box = locate(os.path.join(*filter(None, (HOME, 'boxes', name, version))), '*.box')

        puts_err(colored.blue("Extracting box '{}'...".format(name)))
        os.makedirs('.mech')
        if os.name == 'posix':
            proc = subprocess.Popen(['tar', '-xf', box], cwd='.mech')
            if proc.wait():
                puts_err(colored.red("Cannot extract box"))
                sys.exit(1)
        else:
            tar = tarfile.open(box, 'r')
            tar.extractall('.mech')

    return get_vmx()


def provision_file(vm, source, destination):
    return vm.copyFileFromHostToGuest(source, destination)


def provision_shell(vm, inline, path, args=[]):
    tmp_path = vm.createTempfileInGuest()
    if tmp_path is None:
        return

    try:
        if path and os.path.isfile(path):
            puts_err(colored.blue("Configuring script {}...".format(path)))
            if vm.copyFileFromHostToGuest(path, tmp_path) is None:
                return
        else:
            if path:
                if any(path.startswith(s) for s in ('https://', 'http://', 'ftp://')):
                    puts_err(colored.blue("Downloading {}...".format(path)))
                    try:
                        inline = requests.get(path).read()
                    except requests.ConnectionError:
                        return
                else:
                    puts_err(colored.red("Cannot open {}".format(path)))
                    return

            if not inline:
                puts_err(colored.red("No script to execute"))
                return

            puts_err(colored.blue("Configuring script..."))
            with tempfile.NamedTemporaryFile() as f:
                f.write(inline)
                f.flush()
                if vm.copyFileFromHostToGuest(f.name, tmp_path) is None:
                    return

        puts_err(colored.blue("Configuring environment..."))
        if vm.runScriptInGuest('/bin/sh', "chmod +x '{}'".format(tmp_path)) is None:
            return

        puts_err(colored.blue("Executing program..."))
        return vm.runProgramInGuest(tmp_path, args)

    finally:
        vm.deleteFileInGuest(tmp_path, quiet=True)


def config_ssh_string(config_ssh):
    ssh_config = "Host default" + os.linesep
    for k, v in config_ssh.items():
        ssh_config += "  {} {}".format(k, v) + os.linesep
    return ssh_config
