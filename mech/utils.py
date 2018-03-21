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
from filelock import Timeout, FileLock
from clint.textui import colored, puts_err
from clint.textui import progress


logger = logging.getLogger(__name__)


HOME = os.path.expanduser('~/.mech')
DATA_DIR = os.path.join(HOME, 'data')


def uncomment(text):
    def e(m):
        return '\x00%02x' % ord(m.group(1))
    e.re = re.compile(r'\\(.)', re.DOTALL | re.MULTILINE)

    def r(m):
        s = m.group(0)
        if s.startswith('/'):
            return ''
        if s.startswith(','):
            return s[1:]
        return s
    r.re = re.compile(r'//.*?$|/\*.*?\*/|\'.*?\'|".*?"|,\s*?(?:}|])', re.DOTALL | re.MULTILINE)

    def u(m):
        return '\\%s' % chr(int(m.group(1), 16))
    u.re = re.compile(r'\x00(..)', re.DOTALL | re.MULTILINE)

    return u.re.sub(u, r.re.sub(r, e.re.sub(e, text)))


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


def save_mechfile(mechfile, path):
    with open(os.path.join(path, 'Mechfile'), 'w+') as fp:
        json.dump(mechfile, fp, sort_keys=True, indent=2, separators=(',', ': '))
    return True


def locate(path, glob):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, glob):
                return os.path.abspath(os.path.join(root, filename))


def parse_vmx(path):
    vmx = collections.OrderedDict()
    with open(path) as fp:
        for line in fp:
            line = line.strip().split('=', 1)
            vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def update_vmx(path):
    updated = False

    vmx = parse_vmx(path)

    # Check if there is an existing interface
    has_network = False
    for vmx_key in vmx:
        if vmx_key.startswith('ethernet'):
            has_network = True

    # Write one if there is not
    if not has_network:
        vmx["ethernet0.addresstype"] = "generated"
        vmx["ethernet0.bsdname"] = "en0"
        vmx["ethernet0.connectiontype"] = "nat"
        vmx["ethernet0.displayname"] = "Ethernet"
        vmx["ethernet0.linkstatepropagation.enable"] = "FALSE"
        vmx["ethernet0.pcislotnumber"] = "32"
        vmx["ethernet0.present"] = "TRUE"
        vmx["ethernet0.virtualdev"] = "e1000"
        vmx["ethernet0.wakeonpcktrcv"] = "FALSE"
        puts_err(colored.yellow("Added network interface to vmx file"))
        updated = True

    if updated:
        with open(path, 'w') as new_vmx:
            for key in vmx:
                value = vmx[key]
                row = "{} = {}".format(key, value)
                new_vmx.write(row + os.linesep)

    # puts_err(colored.yellow("Upgrading VM..."))
    # vmrun = VMrun(path)
    # vmrun.upgradevm()


def instances():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    index_path = os.path.join(DATA_DIR, 'index')
    index_lock = os.path.join(DATA_DIR, 'index.lock')
    try:
        with FileLock(index_lock, timeout=3):
            updated = False
            if os.path.exists(index_path):
                with open(index_path) as fp:
                    instances = json.loads(uncomment(fp.read()))
                # prune unexistent Mechfiles
                for k in list(instances):
                    instance_data = instances[k]
                    path = instance_data and instance_data.get('path')
                    if not path or not os.path.exists(os.path.join(path, 'Mechfile')):
                        del instances[k]
                        updated = True
            else:
                instances = {}
            if updated:
                with open(index_path, 'w') as fp:
                    json.dump(instances, fp, sort_keys=True, indent=2, separators=(',', ': '))
            return instances
    except Timeout:
        puts_err(colored.red(textwrap.fill("Couldn't access index, it seems locked.")))
        sys.exit(1)


def settle_instance(instance_name, obj=None, force=False):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    index_path = os.path.join(DATA_DIR, 'index')
    index_lock = os.path.join(DATA_DIR, 'index.lock')
    try:
        with FileLock(index_lock, timeout=3):
            updated = False
            if os.path.exists(index_path):
                with open(index_path) as fp:
                    instances = json.loads(uncomment(fp.read()))
                # prune unexistent Mechfiles
                for k in list(instances):
                    instance_data = instances[k]
                    path = instance_data and instance_data.get('path')
                    if not path or not os.path.exists(os.path.join(path, 'Mechfile')):
                        del instances[k]
                        updated = True
            else:
                instances = {}
            instance_data = instances.get(instance_name)
            if not instance_data or force:
                if obj:
                    instance_data = instances[instance_name] = obj
                    updated = True
                else:
                    instance_data = {}
            if updated:
                with open(index_path, 'w') as fp:
                    json.dump(instances, fp, sort_keys=True, indent=2, separators=(',', ': '))
            return instance_data
    except Timeout:
        puts_err(colored.red(textwrap.fill("Couldn't access index, it seems locked.")))
        sys.exit(1)


def load_mechfile(pwd):
    while pwd:
        mechfile = os.path.join(pwd, 'Mechfile')
        if os.path.isfile(mechfile):
            with open(mechfile) as fp:
                try:
                    return json.loads(uncomment(fp.read()))
                except ValueError:
                    puts_err(colored.red("Invalid Mechfile." + os.linesep))
                    break
        new_pwd = os.path.basename(pwd)
        pwd = None if new_pwd == pwd else new_pwd
    puts_err(colored.red(textwrap.fill(
        "Couldn't find a Mechfile in the current directory any deeper directories. "
        "A Mech environment is required to run this command. Run `mech init` "
        "to create a new Mech environment. Or specify the name of the VM you'd "
        "like to start with `mech up <name>`. A final option is to change to a "
        "directory with a Mechfile and to try again."
    )))
    sys.exit(1)


def build_mechfile(descriptor, name=None, version=None, requests_kwargs={}):
    mechfile = {}
    if descriptor is None:
        return mechfile
    if any(descriptor.startswith(s) for s in ('https://', 'http://', 'ftp://')):
        mechfile['url'] = descriptor
        if not name:
            name = os.path.splitext(os.path.basename(descriptor))[0]
        mechfile['box'] = name
        if version:
            mechfile['box_version'] = version
        return mechfile
    elif os.path.isfile(descriptor):
        try:
            with open(descriptor) as fp:
                catalog = json.loads(uncomment(fp.read()))
        except Exception:
            mechfile['file'] = descriptor
            if not name:
                name = os.path.splitext(os.path.basename(descriptor))[0]
            mechfile['box'] = name
            if version:
                mechfile['box_version'] = version
        return mechfile
    else:
        try:
            account, box, v = (descriptor.split('/', 2) + ['', ''])[:3]
            if not account or not box:
                puts_err(colored.red("Provided box name is not valid"))
            if v:
                version = v
            puts_err(colored.blue("Loading metadata for box '{}'{}".format(descriptor, " ({})".format(version) if version else "")))
            url = 'https://app.vagrantup.com/{}/boxes/{}'.format(account, box)
            r = requests.get(url, **requests_kwargs)
            r.raise_for_status()
            catalog = r.json()
        except (requests.HTTPError, ValueError) as exc:
            puts_err(colored.red("Bad response from HashiCorp's Vagrant Cloud API: %s" % exc))
            sys.exit(1)
        except requests.ConnectionError:
            puts_err(colored.red("Couldn't connect to HashiCorp's Vagrant Cloud API"))
            sys.exit(1)
    return catalog_to_mechfile(catalog, name, version)


def catalog_to_mechfile(catalog, name=None, version=None):
    mechfile = {}
    versions = catalog.get('versions', [])
    for v in versions:
        current_version = v['version']
        if not version or current_version == version:
            for provider in v['providers']:
                if 'vmware' in provider['name']:
                    mechfile['box'] = catalog['name']
                    mechfile['box_version'] = current_version
                    mechfile['url'] = provider['url']
                    return mechfile
    puts_err(colored.red("Couldn't find a VMWare compatible VM for '{}'{}".format(name, " ({})".format(version) if version else "")))
    sys.exit(1)


def init_box(name, version, force=False, save=True, requests_kwargs={}):
    if not os.path.exists('.mech'):
        name_version_box = add_box(name, name=name, version=version, force=force, save=save, requests_kwargs=requests_kwargs)
        if not name_version_box:
            return
        name, version, box = name_version_box
        # box = locate(os.path.join(*filter(None, (HOME, 'boxes', name, version))), '*.box')

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

        if not save and box.startswith(tempfile.gettempdir()):
            os.unlink(box)

    vmx = get_vmx()

    update_vmx(vmx)

    return vmx


def add_box(descriptor, name=None, version=None, force=False, save=True, requests_kwargs={}):
    mechfile = build_mechfile(descriptor, name=name, version=version, requests_kwargs=requests_kwargs)
    return add_mechfile(mechfile, name=name, version=version, force=force, save=save, requests_kwargs=requests_kwargs)


def add_mechfile(mechfile, name=None, version=None, force=False, save=True, requests_kwargs={}):
    url = mechfile.get('url')
    file = mechfile.get('file')
    name = mechfile.get('box')
    version = mechfile.get('box_version')
    if file:
        return add_box_file(name, version, file, force=force, save=save)
    if url:
        return add_box_url(name, version, url, force=force, save=save, requests_kwargs=requests_kwargs)
    puts_err(colored.red("Couldn't find a VMWare compatible VM for '{}'{}".format(name, " ({})".format(version) if version else "")))


def add_box_url(name, version, url, force=False, save=True, requests_kwargs={}):
    boxname = os.path.basename(url)
    box = os.path.join(*filter(None, (HOME, 'boxes', name, version, boxname)))
    exists = os.path.exists(box)
    if not exists or force:
        if exists:
            puts_err(colored.blue("Attempting to download box '{}'...".format(name)))
        else:
            puts_err(colored.blue("Box '{}' could not be found. Attempting to download...".format(name)))
        try:
            puts_err(colored.blue("URL: {}".format(url)))
            r = requests.get(url, stream=True, **requests_kwargs)
            r.raise_for_status()
            try:
                length = int(r.headers['content-length'])
                progress_args = dict(expected_size=length // 1024 + 1)
                progress_type = progress.bar
            except KeyError:
                progress_args = dict(every=1024 * 100)
                progress_type = progress.dots
            with tempfile.NamedTemporaryFile(delete=save) as fp:
                for chunk in progress_type(r.iter_content(chunk_size=1024), label="{} ".format(boxname), **progress_args):
                    if chunk:
                        fp.write(chunk)
                fp.flush()
                if r.headers.get('content-type') == 'application/json':
                    # Downloaded URL might be a Vagrant catalog if it's json:
                    fp.seek(0)
                    catalog = json.loads(fp.read())
                    mechfile = catalog_to_mechfile(catalog, name, version)
                    return add_mechfile(mechfile, name=name, version=version, force=force, save=save, requests_kwargs=requests_kwargs)
                else:
                    # Otherwise it must be a valid box:
                    return add_box_file(name, version, fp.name, url=url, force=force, save=save)
        except requests.HTTPError as exc:
            puts_err(colored.red("Bad response: %s" % exc))
            sys.exit(1)
        except requests.ConnectionError:
            puts_err(colored.red("Couldn't connect to '%s'" % url))
            sys.exit(1)
    return name, version, box


def add_box_file(name, version, filename, url=None, force=False, save=True):
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
                    "This box is comprised of filenames starting with '/' or '..' "
                    "Exiting for the safety of your files."
                )))
                sys.exit(1)

    if valid_tar:
        if save:
            boxname = os.path.basename(url if url else filename)
            box = os.path.join(*filter(None, (HOME, 'boxes', name, version, boxname)))
            path = os.path.dirname(box)
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(box) or force:
                copyfile(filename, box)
        else:
            box = filename
        return name, version, box


def index_active_instance(instance_name):
    path = os.getcwd()
    instance = settle_instance(instance_name, {
        'path': path,
    })
    if instance.get('path') != path:
        puts_err(colored.red(textwrap.fill((
            "There is already a Mech box with the name '{}' at {}"
        ).format(instance_name, instance.get('path')))))
        sys.exit(1)
    return path


def init_mechfile(instance_name, descriptor, name=None, version=None, requests_kwargs={}):
    path = index_active_instance(instance_name)
    mechfile = build_mechfile(descriptor, name=name, version=version, requests_kwargs=requests_kwargs)
    mechfile['name'] = instance_name
    return save_mechfile(mechfile, path)


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
    return vmx


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
                        r = requests.get(path)
                        r.raise_for_status()
                        inline = r.read()
                    except requests.HTTPError:
                        return
                    except requests.ConnectionError:
                        return
                else:
                    puts_err(colored.red("Cannot open {}".format(path)))
                    return

            if not inline:
                puts_err(colored.red("No script to execute"))
                return

            puts_err(colored.blue("Configuring script..."))
            with tempfile.NamedTemporaryFile() as fp:
                fp.write(inline)
                fp.flush()
                if vm.copyFileFromHostToGuest(fp.name, tmp_path) is None:
                    return

        puts_err(colored.blue("Configuring environment..."))
        if vm.runScriptInGuest('/bin/sh', "chmod +x '{}'".format(tmp_path)) is None:
            return

        puts_err(colored.blue("Executing program..."))
        return vm.runProgramInGuest(tmp_path, args)

    finally:
        vm.deleteFileInGuest(tmp_path, quiet=True)


def config_ssh_string(config_ssh):
    ssh_config = "Host {}".format(config_ssh['Host']) + os.linesep
    for k, v in config_ssh.items():
        if k != 'Host':
            ssh_config += "  {} {}".format(k, v) + os.linesep
    return ssh_config
