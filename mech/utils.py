# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
# Copyright (c) 2020 Mike Kinney
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

"""Mech utility functions."""

from __future__ import division, absolute_import

import os
import re
import random
import string
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
from clint.textui import colored
from clint.textui import progress

from .vmrun import VMrun
from .compat import b2s, PY3, raw_input

LOGGER = logging.getLogger(__name__)


def main_dir():
    """Return the main directory."""
    return os.getcwd()


def mech_dir():
    """Return the mech directory."""
    return os.path.join(main_dir(), '.mech')


def makedirs(name, mode=0o777):
    """Make directories with mode supplied."""
    try:
        os.makedirs(name, mode)
    except OSError:
        pass


def confirm(prompt, default='y'):
    """Confirmation prompt."""
    default = default.lower()
    if default not in ['y', 'n']:
        default = 'y'
    choicebox = '[Y/n]' if default == 'y' else '[y/N]'
    prompt = prompt + ' ' + choicebox + ' '

    while True:
        some_input = raw_input(prompt).strip()
        if some_input == '':
            if default == 'y':
                return True
            else:
                return False

        if re.match('y(?:es)?', some_input, re.IGNORECASE):
            return True

        elif re.match('n(?:o)?', some_input, re.IGNORECASE):
            return False


def save_mechfile_entry(mechfile_entry, name, mechfile_should_exist=False):
    """Save the entry to the Mechfile."""
    LOGGER.debug('mechfile_entry:%s name:%s mechfile_should_exist:%s',
                 mechfile_entry, name, mechfile_should_exist)
    mechfile = load_mechfile(mechfile_should_exist)

    mechfile[name] = mechfile_entry

    LOGGER.debug("after adding name:%s mechfile:%s", name, mechfile)
    return save_mechfile(mechfile)


def remove_mechfile_entry(name, mechfile_should_exist=True):
    """Removed the entry from the Mechfile."""
    LOGGER.debug('name:%s mechfile_should_exist:%s', name, mechfile_should_exist)
    mechfile = load_mechfile(mechfile_should_exist)

    if mechfile.get(name):
        del mechfile[name]

    LOGGER.debug("after removing name:%s mechfile:%s", name, mechfile)
    return save_mechfile(mechfile)


def save_mechfile(mechfile):
    """Save the mechfile object (which is a dict) to a file called 'Mechfile'.
       Return True if save was successful.
    """
    LOGGER.debug('mechfile:%s', mechfile)
    with open(os.path.join(main_dir(), 'Mechfile'), 'w+') as the_file:
        json.dump(mechfile, the_file, sort_keys=True, indent=2, separators=(',', ': '))
    return True


def locate(path, glob):
    """Locate a file in the path provided."""
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, glob):
                return os.path.abspath(os.path.join(root, filename))


def parse_vmx(path):
    """Parse the virtual machine configuration (.vmx) file and return an
       ordered dictionary.
    """
    vmx = collections.OrderedDict()
    with open(path) as the_file:
        for line in the_file:
            line = line.strip().split('=', 1)
            if len(line) > 1:
                vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def update_vmx(path, numvcpus=None, memsize=None, no_nat=False):
    """Update the virtual machine configuration (.vmx)
       file with desired settings.
    """
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
        if not no_nat:
            vmx["ethernet0.connectiontype"] = "nat"
        vmx["ethernet0.displayname"] = "Ethernet"
        vmx["ethernet0.linkstatepropagation.enable"] = "FALSE"
        vmx["ethernet0.pcislotnumber"] = "32"
        vmx["ethernet0.present"] = "TRUE"
        vmx["ethernet0.virtualdev"] = "e1000"
        vmx["ethernet0.wakeonpcktrcv"] = "FALSE"
        print(colored.yellow("Added network interface to vmx file"))
        updated = True

    # write out vmx file if memsize or numvcpus was specified
    if numvcpus is not None:
        vmx["numvcpus"] = '"{}"'.format(numvcpus)
        updated = True

    if memsize is not None:
        vmx["memsize"] = '"{}"'.format(memsize)
        updated = True

    if updated:
        with open(path, 'w') as new_vmx:
            for key in vmx:
                value = vmx[key]
                row = "{} = {}".format(key, value)
                new_vmx.write(row + os.linesep)


def load_mechfile(should_exist=True):
    """Load the Mechfile from disk and return the mechfile as a dictionary."""
    mechfile_fullpath = os.path.join(main_dir(), 'Mechfile')
    LOGGER.debug("mechfile_fullpath:%s", mechfile_fullpath)
    if os.path.isfile(mechfile_fullpath):
        with open(mechfile_fullpath) as the_file:
            try:
                mechfile = json.loads(the_file.read())
                LOGGER.debug('mechfile:%s', mechfile)
                return mechfile
            except ValueError:
                print(colored.red("Invalid Mechfile." + os.linesep))
                return {}
    else:
        if should_exist:
            sys.exit(colored.red(textwrap.fill(
                     "Could not find a Mechfile in the current directory. "
                     "A Mech environment is required to run this command. Run `mech init` "
                     "to create a new Mech environment. Or specify the name of the VM you would "
                     "like to start with `mech up <name>`. A final option is to change to a "
                     "directory with a Mechfile and to try again.")))
        else:
            return {}


def default_shared_folders():
    """Return the default shared folders config.
       The host_path value of "../.." is because it is relative to the vmx file.
    """
    return [{'share_name': 'mech', 'host_path': '../..'}]


def build_mechfile_entry(location, box=None, name=None, box_version=None,
                         shared_folders=None):
    """Build the Mechfile from the inputs."""
    LOGGER.debug("location:%s name:%s box:%s box_version:%s", location, name, box, box_version)
    mechfile_entry = {}

    if location is None:
        return mechfile_entry

    mechfile_entry['name'] = name
    mechfile_entry['box'] = box
    mechfile_entry['box_version'] = box_version

    if shared_folders is None:
        shared_folders = default_shared_folders()
    mechfile_entry['shared_folders'] = shared_folders

    if any(location.startswith(s) for s in ('https://', 'http://', 'ftp://')):
        if not name:
            name = 'first'
        mechfile_entry['url'] = location
        return mechfile_entry

    elif location.startswith('file:') or os.path.isfile(re.sub(r'^file:(?://)?', '', location)):
        if not name:
            name = 'first'
        location = re.sub(r'^file:(?://)?', '', location)
        LOGGER.debug('location:%s', location)
        mechfile_entry['file'] = location
        try:
            # see if the location/file is a json file
            with open(location) as the_file:
                # if an exception is not thrown, then set values and continue
                # to the end of the function
                catalog = json.loads(the_file.read())
                LOGGER.debug('catalog:%s', catalog)
        except (json.decoder.JSONDecodeError, ValueError) as e:
            # this means the location/file is probably a .box file
            # or the json is invalid
            LOGGER.debug('mechfile_entry:%s', mechfile_entry)
            LOGGER.debug(e)
            return mechfile_entry
        except IOError:
            # cannot open file
            sys.exit('Error: Cannot open file:({})'.format(location))
    else:
        try:
            account, box, ver = (location.split('/', 2) + ['', ''])[:3]
            if not account or not box:
                sys.exit(colored.red("Provided box name is not valid"))
            if ver:
                box_version = ver
            print(
                colored.blue("Loading metadata for box '{}'{}".format(
                    location, " ({})".format(box_version) if box_version else "")))
            url = 'https://app.vagrantup.com/{}/boxes/{}'.format(account, box)
            response = requests.get(url)
            response.raise_for_status()
            catalog = response.json()
        except (requests.HTTPError, ValueError) as exc:
            sys.exit(colored.red("Bad response from HashiCorp's Vagrant Cloud API: %s" % exc))
        except requests.ConnectionError:
            sys.exit(colored.red("Couldn't connect to HashiCorp's Vagrant Cloud API"))

    LOGGER.debug("catalog:%s name:%s box_version:%s", catalog, name, box_version)
    return catalog_to_mechfile(catalog, name=name, box=box, box_version=box_version)


def catalog_to_mechfile(catalog, name=None, box=None, box_version=None):
    """Convert the Hashicorp cloud catalog entry to Mechfile entry."""
    LOGGER.debug('catalog:%s name:%s box:%s box_version:%s', catalog, name, box, box_version)
    mechfile = {}
    versions = catalog.get('versions', [])
    for ver in versions:
        current_version = ver['version']
        if not box_version or current_version == box_version:
            for provider in ver['providers']:
                if 'vmware' in provider['name']:
                    mechfile['name'] = name
                    mechfile['box'] = catalog['name']
                    mechfile['box_version'] = current_version
                    mechfile['url'] = provider['url']
                    mechfile['shared_folders'] = default_shared_folders()
                    return mechfile
    sys.exit(colored.red("Couldn't find a VMWare compatible VM using catalog:{}".format(catalog)))


def tar_cmd(*args, **kwargs):
    """Build the tar command to be used to extract the box."""
    try:
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(['tar', '--help'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, startupinfo=startupinfo)
    except OSError:
        return None
    if proc.returncode:
        return None
    stdoutdata, _ = map(b2s, proc.communicate())
    tar = ['tar']
    if kwargs.get('wildcards') and re.search(r'--wildcards\b', stdoutdata):
        tar.append('--wildcards')
    if kwargs.get('force_local') and re.search(r'--force-local\b', stdoutdata):
        tar.append('--force-local')
    if kwargs.get('fast_read') and sys.platform.startswith('darwin'):
        tar.append('--fast-read')
    tar.extend(args)
    return tar


def init_box(name, box=None, box_version=None, location=None, force=False, save=True,
             instance_path=None, numvcpus=None, memsize=None, no_nat=False):
    """Initialize the box. This includes uncompressing the files
       from the box file and updating the vmx file with
       desired settings. Return the full path to the vmx file.
    """
    LOGGER.debug("name:%s box:%s box_version:%s location:%s", name, box, box_version, location)
    if not locate(instance_path, '*.vmx'):
        name_version_box = add_box(
            name=name,
            box=box,
            box_version=box_version,
            location=location,
            force=force,
            save=save)
        if not name_version_box:
            sys.exit(colored.red("Cannot find a valid box with a VMX file in it"))

        box_parts = box.split('/')
        box_dir = os.path.join(*filter(None, (mech_dir(), 'boxes',
                                              box_parts[0], box_parts[1], box_version)))
        box_file = locate(box_dir, '*.box')

        print(colored.blue("Extracting box '{}'...".format(box_file)))
        makedirs(instance_path)
        if sys.platform == 'win32':
            cmd = tar_cmd('-xf', box_file, force_local=True)
        else:
            cmd = tar_cmd('-xf', box_file)
        if cmd:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(cmd, cwd=instance_path, startupinfo=startupinfo)
            if proc.wait():
                sys.exit(colored.red("Cannot extract box"))
        else:
            tar = tarfile.open(box_file, 'r')
            tar.extractall(instance_path)

        if not save and box.startswith(tempfile.gettempdir()):
            os.unlink(box)

    vmx_path = locate(instance_path, '*.vmx')
    if not vmx_path:
        sys.exit(colored.red("Cannot locate a VMX file"))

    update_vmx(vmx_path, numvcpus=numvcpus, memsize=memsize, no_nat=no_nat)
    return vmx_path


def add_box(name=None, box=None, box_version=None, location=None,
            force=False, save=True):
    """Add a box."""
    # build the dict
    LOGGER.debug('name:%s box:%s box_version:%s location:%s', name,
                 box, box_version, location)
    mechfile_entry = build_mechfile_entry(
        box=box,
        name=name,
        location=location,
        box_version=box_version)

    return add_mechfile(
        mechfile_entry,
        name=name,
        box=box,
        location=location,
        box_version=box_version,
        force=force,
        save=save)


def add_mechfile(mechfile_entry, name=None, box=None, box_version=None,
                 location=None, force=False, save=True):
    """Add a mechfile entry."""
    LOGGER.debug('mechfile_entry:%s name:%s box:%s box_version:%s location:%s',
                 mechfile_entry, name, box, box_version, location)

    box = mechfile_entry.get('box')
    name = mechfile_entry.get('name')
    box_version = mechfile_entry.get('box_version')

    url = mechfile_entry.get('url')
    box_file = mechfile_entry.get('file')

    if box_file:
        return add_box_file(box=box, box_version=box_version, filename=box_file,
                            force=force, save=save)

    if url:
        return add_box_url(name=name, box=box, box_version=box_version,
                           url=url, force=force, save=save)
    print(
        colored.red(
            "Could not find a VMWare compatible VM for '{}'{}".format(
                name, " ({})".format(box_version) if box_version else "")))


def add_box_url(name, box, box_version, url, force=False, save=True):
    """Add a box using the URL."""
    LOGGER.debug('name:%s box:%s box_version:%s url:%s', name, box, box_version, url)
    boxname = os.path.basename(url)
    box_parts = box.split('/')
    first_box_part = box_parts[0]
    second_box_part = ''
    if len(box_parts) > 1:
        second_box_part = box_parts[1]
    box_dir = os.path.join(*filter(None, (mech_dir(), 'boxes',
                                          first_box_part, second_box_part, box_version)))
    exists = os.path.exists(box_dir)
    if not exists or force:
        if exists:
            print(colored.blue("Attempting to download box '{}'...".format(box)))
        else:
            print(colored.blue("Box '{}' could not be found. "
                               "Attempting to download...".format(box)))
        try:
            print(colored.blue("URL: {}".format(url)))
            response = requests.get(url, stream=True)
            response.raise_for_status()
            try:
                length = int(response.headers['content-length'])
                progress_args = dict(expected_size=length // 1024 + 1)
                progress_type = progress.bar
            except KeyError:
                progress_args = dict(every=1024 * 100)
                progress_type = progress.dots
            the_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                for chunk in progress_type(
                        response.iter_content(
                            chunk_size=1024),
                        label="{} ".format(boxname),
                        **progress_args):
                    if chunk:
                        the_file.write(chunk)
                the_file.close()
                if response.headers.get('content-type') == 'application/json':
                    # Downloaded URL might be a Vagrant catalog if it's json:
                    catalog = json.load(the_file.name)
                    mechfile = catalog_to_mechfile(catalog, name, box, box_version)
                    return add_mechfile(
                        mechfile,
                        name=name,
                        box_version=box_version,
                        force=force,
                        save=save)
                else:
                    # Otherwise it must be a valid box:
                    return add_box_file(box=box, box_version=box_version,
                                        filename=the_file.name, url=url, force=force,
                                        save=save)
            finally:
                os.unlink(the_file.name)
        except requests.HTTPError as exc:
            sys.exit(colored.red("Bad response: %s" % exc))
        except requests.ConnectionError:
            sys.exit(colored.red("Couldn't connect to '%s'" % url))
    return name, box_version, box


def add_box_file(box=None, box_version=None, filename=None, url=None, force=False, save=True):
    """Add a box using a file as the source. Returns box and box_version."""
    print(colored.blue("Checking box '{}' integrity filename:{}...".format(box, filename)))

    if sys.platform == 'win32':
        cmd = tar_cmd('-tf', filename, '*.vmx', wildcards=True, fast_read=True, force_local=True)
    else:
        cmd = tar_cmd('-tf', filename, '*.vmx', wildcards=True, fast_read=True)
    if cmd:
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, startupinfo=startupinfo)
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
                sys.exit(colored.red(textwrap.fill(
                         "This box is comprised of filenames starting with '/' or '..' "
                         "Exiting for the safety of your files.")))

    if valid_tar:
        if save:
            boxname = os.path.basename(url if url else filename)
            box = os.path.join(*filter(None, (mech_dir(), 'boxes', box, box_version, boxname)))
            path = os.path.dirname(box)
            makedirs(path)
            if not os.path.exists(box) or force:
                copyfile(filename, box)
        else:
            box = filename
        return box, box_version


def get_info_for_auth(mech_use=False):
    """Get information (username/pub_key) for authentication."""
    username = os.getlogin()
    pub_key = os.path.expanduser('~/.ssh/id_rsa.pub')
    return {'auth': {'username': username, 'pub_key': pub_key, 'mech_use': mech_use}}


def init_mechfile(location=None, box=None, name=None, box_version=None, add_me=None,
                  use_me=None):
    """Initialize the Mechfile."""
    LOGGER.debug("name:%s box:%s box_version:%s location:%s add_me:%s use_me:%s",
                 name, box, box_version, location, add_me, use_me)
    mechfile_entry = build_mechfile_entry(
        location=location,
        box=box,
        name=name,
        box_version=box_version)
    if add_me:
        mechfile_entry.update(get_info_for_auth(use_me))
    LOGGER.debug('mechfile_entry:%s', mechfile_entry)
    return save_mechfile_entry(mechfile_entry, name, mechfile_should_exist=False)


def add_to_mechfile(location=None, box=None, name=None, box_version=None, add_me=None,
                    use_me=None):
    """Add entry to the Mechfile."""
    LOGGER.debug("name:%s box:%s box_version:%s location:%s add_me:%s use_me:%s",
                 name, box, box_version, location, add_me, use_me)
    this_mech_entry = build_mechfile_entry(
        location=location,
        box=box,
        name=name,
        box_version=box_version)
    if add_me:
        this_mech_entry.update(get_info_for_auth(use_me))
    LOGGER.debug('this_mech_entry:%s', this_mech_entry)
    return save_mechfile_entry(this_mech_entry, name, mechfile_should_exist=False)


def random_string(string_len=15):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_len))


def add_auth(instance):
    """Add authentication to VM."""

    if not instance:
        sys.exit(colored.red("Need to provide an instance to add_auth()."))

    if instance.vmx is None or instance.user is None or instance.password is None:
        sys.exit(colored.red("Need to provide vmx/user/password to add_auth()."))

    print(colored.green('Adding auth to instance:{}'.format(instance.name)))

    vmrun = VMrun(instance.vmx, instance.user, instance.password)
    # cannot run if vmware tools are not installed
    if not vmrun.installed_tools():
        sys.exit(colored.red("Cannot add auth if VMware Tools are not installed."))

    if instance.auth:
        username = instance.auth.get('username', None)
        pub_key = instance.auth.get('pub_key', None)
        if username and pub_key:
            with open(pub_key, 'r') as the_file:
                pub_key_contents = the_file.read().strip()
            if pub_key_contents:
                # set the password to some random string
                # user should never need it (sudo should not prompt for a
                # password)
                password = random_string()
                cmd = ('sudo useradd -m -s /bin/bash -p "{password}" {username};'
                       'sudo mkdir /home/{username}/.ssh;'
                       'sudo usermod -aG sudo {username};'
                       'echo "{username} ALL=(ALL) NOPASSWD: ALL" | '
                       'sudo tee -a /etc/sudoers;'
                       'echo "{pub_key_contents}" | '
                       'sudo tee -a /home/{username}/.ssh/authorized_keys;'
                       'sudo chmod 700 /home/{username}/.ssh;'
                       'sudo chown {username}:{username} /home/{username}/.ssh;'
                       'sudo chmod 600 /home/{username}/.ssh/authorized_keys;'
                       'sudo chown {username}:{username} /home/{username}/.ssh/authorized_keys'
                       ).format(username=username, pub_key_contents=pub_key_contents,
                                password=password)
                LOGGER.debug('cmd:', cmd)
                results = vmrun.run_script_in_guest('/bin/sh', cmd, quiet=True)
                LOGGER.debug('results:%s', results)
                if results is None:
                    print(colored.red("Did not add auth"))
                else:
                    print(colored.green("Added auth."))
            else:
                print(colored.green("Could not read contents of the pub_key"
                                    " file:{}".format(pub_key)))
        else:
            print(colored.blue("Warning: Need a username and pub_key in auth."))
    else:
        print(colored.blue("No auth to add."))


def ssh(instance, command, plain=None, extra=None):
    """Run ssh command.
       Note: May not really need the tempfile if self.use_psk==True.
             Using the tempfile, there are options to not add host to the known_hosts files
             which is useful, but could be MITM attacks. Not likely locally, but still
             could be an issue.
    """
    LOGGER.debug('command:%s plain:%s extra:%s', command, plain, extra)
    if instance.created:
        config_ssh = instance.config_ssh()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp_file.write(config_ssh_string(config_ssh).encode('utf-8'))
            temp_file.close()

            cmds = ['ssh']
            if not plain:
                cmds.extend(('-F', temp_file.name))
            if extra:
                cmds.extend(extra)
            if not plain:
                cmds.append(config_ssh['Host'])
            if command:
                cmds.extend(('--', command))

            LOGGER.debug(
                " ".join(
                    "'{}'".format(
                        c.replace(
                            "'",
                            "\\'")) if ' ' in c else c for c in cmds))

            # if running a script
            if command:
                result = subprocess.run(cmds, capture_output=True)
                stdout = result.stdout.decode('utf-8').strip()
                stderr = result.stderr.decode('utf-8').strip()
                return result.returncode, stdout, stderr
            else:
                # interactive
                return subprocess.call(cmds), None, None
        finally:
            os.unlink(temp_file.name)


def scp(instance, src, dst, dst_is_host, extra=None):
    """Run scp command.
       Note: May not really need the tempfile if self.use_psk==True.
             Using the tempfile, there are options to not add host to the known_hosts files
             which is useful, but could be MITM attacks. Not likely locally, but still
             could be an issue.
    """
    if instance.created:

        config_ssh = instance.config_ssh()
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            temp_file.write(config_ssh_string(config_ssh).encode())
            temp_file.close()

            cmds = ['scp']
            cmds.extend(('-F', temp_file.name))
            if extra:
                cmds.extend(extra)

            host = config_ssh['Host']
            dst = '{}:{}'.format(host, dst) if dst_is_host else dst
            src = '{}:{}'.format(host, src) if not dst_is_host else src
            cmds.extend((src, dst))

            LOGGER.debug(
                " ".join(
                    "'{}'".format(
                        c.replace(
                            "'",
                            "\\'")) if ' ' in c else c for c in cmds))
            return subprocess.run(cmds, capture_output=True)
        finally:
            os.unlink(temp_file.name)


def del_user(instance, username):
    """Delete a user in guest VM."""

    if not instance:
        sys.exit(colored.red("Need to provide an instance to del_user()."))

    if instance.vmx is None:
        sys.exit(colored.red("VM must be created."))

    if instance.user is None:
        sys.exit(colored.red("A user is required."))

    print(colored.green('Removing username ({}) from instance:{}...'.format(username,
                                                                            instance.name)))

    cmd = 'sudo userdel -fr vagrant'
    LOGGER.debug('cmd:', cmd)

    if instance.use_psk:
        ssh(instance, cmd)
    else:
        vmrun = VMrun(instance.vmx, user=instance.user,
                      password=instance.password, use_psk=instance.use_psk)
        # cannot run if vmware tools are not installed
        if not vmrun.installed_tools():
            sys.exit(colored.red("Cannot add del_user if VMware Tools are not installed."))
        results = vmrun.run_script_in_guest('/bin/sh', cmd, quiet=True)
        LOGGER.debug('results:%s', results)
        if results is None:
            print(colored.red("Failed running del_user()."))
        else:
            print(colored.green("Success running del_user()."))


def provision(instance, show=False):
    """Provision an instance.

    Args:
        instance (MechInstance): an instance
        show (bool): just print the provisioning

    Notes:
        Valid provision types are:
           file: copies files to instances
           shell: executes scripts

    """

    if not instance:
        sys.exit(colored.red("Need to provide an instance to provision()."))

    if instance.vmx is None or instance.user is None:
        sys.exit(colored.red("Need to provide vmx/user to provision()."))

    print(colored.green('Provisioning instance:{}'.format(instance.name)))

    vmrun = VMrun(instance.vmx, instance.user, instance.password)
    # cannot run provisioning if vmware tools are not installed
    if not vmrun.installed_tools():
        sys.exit(colored.red("Cannot provision if VMware Tools are not installed."))

    provisioned = 0
    if instance.provision:
        for i, pro in enumerate(instance.provision):
            provision_type = pro.get('type')
            if provision_type == 'file':
                source = pro.get('source')
                destination = pro.get('destination')
                if show:
                    print(colored.green("instance:{} provision_type:{} source:{} "
                                        "destination:{}".format(instance.name, provision_type,
                                                                source, destination)))
                else:
                    results = provision_file(vmrun, instance, source, destination)
                    LOGGER.debug('results:%s', results)
                    if results is None:
                        print(colored.red("Not Provisioned"))
                        return
                provisioned += 1

            elif provision_type == 'shell':
                inline = pro.get('inline')
                path = pro.get('path')

                args = pro.get('args')
                if not isinstance(args, list):
                    args = [args]
                if show:
                    print(colored.green(" instance:{} provision_type:{} inline:{} path:{} "
                                        "args:{}".format(instance.name, provision_type,
                                                         inline, path, args)))
                else:
                    if provision_shell(vmrun, instance, inline, path, args) is None:
                        print(colored.red("Not Provisioned"))
                        return
                provisioned += 1

            else:
                print(colored.red("Not Provisioned ({}".format(i)))
                return
        else:
            print(colored.green("VM ({}) Provision {} "
                                "entries".format(instance.name, provisioned)))
    else:
        print(colored.blue("Nothing to provision"))


def provision_file(vmrun, instance, source, destination):
    """Provision from file.

    Args:
        vmrun (VMrun): instance of the VMrun class
        source (str): full path of a file to copy
        source (str): full path where the file is to be copied to

    Notes:
       This function copies a file from host to guest.

    """
    print(colored.blue("Copying ({}) to ({})".format(source, destination)))
    if instance.use_psk:
        results = scp(instance, source, destination, True)
    else:
        results = vmrun.copy_file_from_host_to_guest(source, destination)
    return results


def create_tempfile_in_guest(instance):
    """Create a tempfile in the guest."""
    cmd = 'tmpfile=$(mktemp); echo $tmpfile'
    _, stdout, _ = ssh(instance, cmd)
    return stdout


def provision_shell(vmrun, instance, inline, script_path, args=None):
    """Provision from shell.

    Args:
        vmrun (VMrun): instance of the VMrun class
        instance (MechInstance): instance of the MechInstance class
        inline (bool): run the script inline
        script_path (str): path to the script to run
        args (list of str): arguments to the script

    """
    if args is None:
        args = []
    if instance.use_psk:
        tmp_path = create_tempfile_in_guest(instance)
    else:
        tmp_path = vmrun.create_tempfile_in_guest()
    LOGGER.debug('inline:%s script_path:%s args:%s tmp_path:%s',
                 inline, script_path, args, tmp_path)
    if tmp_path is None:
        print(colored.red("Warning: Could not create tempfile in guest."))
        return

    try:
        if script_path and os.path.isfile(script_path):
            print(colored.blue("Configuring script {}...".format(script_path)))
            if instance.use_psk:
                results = scp(instance, script_path, tmp_path, True)
                if results is None:
                    print(colored.red("Warning: Could not copy file to guest."))
                    return
            else:
                if vmrun.copy_file_from_host_to_guest(script_path, tmp_path) is None:
                    print(colored.red("Warning: Could not copy file to guest."))
                    return
        else:
            if script_path:
                if any(script_path.startswith(s) for s in ('https://', 'http://', 'ftp://')):
                    print(colored.blue("Downloading {}...".format(script_path)))
                    try:
                        response = requests.get(script_path)
                        response.raise_for_status()
                        inline = response.read()
                    except requests.HTTPError:
                        return
                    except requests.ConnectionError:
                        return
                else:
                    print(colored.red("Cannot open {}".format(script_path)))
                    return

            if not inline:
                print(colored.red("No script to execute"))
                return

            print(colored.blue("Configuring script to run inline..."))
            the_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                the_file.write(str.encode(inline))
                the_file.close()
                if instance.use_psk:
                    scp(instance, the_file.name, tmp_path, True)
                else:
                    if vmrun.copy_file_from_host_to_guest(the_file.name, tmp_path) is None:
                        return
            finally:
                os.unlink(the_file.name)

        print(colored.blue("Configuring environment..."))
        make_executable = "chmod +x '{}'".format(tmp_path)
        LOGGER.debug('make_executable:%s', make_executable)
        if instance.use_psk:
            if ssh(instance, make_executable) is None:
                print(colored.red("Warning: Could not configure script in the environment."))
                return
        else:
            if vmrun.run_script_in_guest('/bin/sh', make_executable) is None:
                print(colored.red("Warning: Could not configure script in the environment."))
                return

        print(colored.blue("Executing program..."))
        if instance.use_psk:
            args_string = ' '.join([str(elem) for elem in args])
            LOGGER.debug('args:%s args_string:%s', args, args_string)
            return ssh(instance, tmp_path, args_string)
        else:
            return vmrun.run_program_in_guest(tmp_path, args)

    finally:
        if instance.use_psk:
            return ssh(instance, 'rm -f "{}"'.format(tmp_path))
        else:
            vmrun.delete_file_in_guest(tmp_path, quiet=True)


def config_ssh_string(config_ssh):
    """Build the ssh-config string from a dict holding the keys/values."""
    ssh_config = "Host {}".format(config_ssh.get('Host', '')) + os.linesep
    for key, value in config_ssh.items():
        if key != 'Host':
            ssh_config += "  {} {}".format(key, value) + os.linesep
    return ssh_config


def share_folders(vmrun, inst):
    """Share folders.
    Args:
        vmrun (VMrun): an instance of the VMrun class
        inst (MechInstance): an instance of the MechInstance class (representing a vm)

    """
    print(colored.blue("Sharing folders..."))
    vmrun.enable_shared_folders(quiet=False)
    for share in inst.shared_folders:
        share_name = share.get('share_name')
        host_path = share.get('host_path')
        print(colored.blue("share:{} host_path:{}".format(share_name, host_path)))
        vmrun.add_shared_folder(share_name, host_path, quiet=True)


def get_fallback_executable():
    """Get a fallback executable for the command line tool 'vmrun'."""
    if 'PATH' in os.environ:
        LOGGER.debug("os.environ['PATH']:%s", os.environ['PATH'])
        for path in os.environ['PATH'].split(os.pathsep):
            vmrun = os.path.join(path, 'vmrun')
            if os.path.exists(vmrun):
                return vmrun
            vmrun = os.path.join(path, 'vmrun.exe')
            if os.path.exists(vmrun):
                return vmrun
    return None


def get_darwin_executable():
    """Get the full path for the 'vmrun' command on a mac host."""
    vmrun = '/Applications/VMware Fusion.app/Contents/Library/vmrun'
    if os.path.exists(vmrun):
        return vmrun
    return get_fallback_executable()


def get_win32_executable():
    """Get the full path for the 'vmrun' command on a Windows host."""
    if PY3:
        import winreg
    else:
        import _winreg as winreg
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        key = winreg.OpenKey(reg, 'SOFTWARE\\VMware, Inc.\\VMware Workstation')
        try:
            return os.path.join(winreg.QueryValueEx(key, 'InstallPath')[0], 'vmrun.exe')
        finally:
            winreg.CloseKey(key)
    except WindowsError:
        key = winreg.OpenKey(reg, 'SOFTWARE\\WOW6432Node\\VMware, Inc.\\VMware Workstation')
        try:
            return os.path.join(winreg.QueryValueEx(key, 'InstallPath')[0], 'vmrun.exe')
        finally:
            winreg.CloseKey(key)
    finally:
        reg.Close()
    return get_fallback_executable()


def get_provider(vmrun_executable):
    """
    Identifies the right hosttype for vmrun command (ws | fusion | player)
    """

    if sys.platform == 'darwin':
        return 'fusion'

    for provider in ['ws', 'player', 'fusion']:
        # To determine the provider, try
        # running the vmrun command to see which one works.
        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen([vmrun_executable,
                                     '-T',
                                     provider,
                                     'list'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    startupinfo=startupinfo)
        except OSError:
            pass

        map(b2s, proc.communicate())
        if proc.returncode == 0:
            return provider
