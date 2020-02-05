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

from __future__ import division, absolute_import

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

from .compat import raw_input, b2s
from .vmrun import VMrun

logger = logging.getLogger(__name__)


MAIN_DIR = os.path.expanduser(os.getcwd())


def main_dir():
    """Return the main directory."""
    return MAIN_DIR


def mech_dir():
    """Return the mech directory."""
    return os.path.join(MAIN_DIR, '.mech')


def makedirs(name, mode=0o777):
    """Make directories with mode supplied."""
    try:
        os.makedirs(name, mode)
    except OSError:
        pass


def uncomment(text):
    """Uncomment a line of text."""
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
    """Confirmation prompt."""
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


def save_mechfile_entry(mechfile_entry, name, mechfile_should_exist=False):
    """Save the entry to the Mechfile."""
    logger.debug('mechfile_entry:{} name:{} '
                 'mechfile_should_exist:{}'.format(mechfile_entry, name,
                                                   mechfile_should_exist))
    mechfile = load_mechfile(mechfile_should_exist)

    mechfile[name] = mechfile_entry

    logger.debug("after adding name:{} mechfile:{}".format(name, mechfile))
    return save_mechfile(mechfile)


def remove_mechfile_entry(name, mechfile_should_exist=True):
    """Removed the entry from the Mechfile."""
    logger.debug('name:{} mechfile_should_exist:{}'.format(name, mechfile_should_exist))
    mechfile = load_mechfile(mechfile_should_exist)

    if mechfile.get(name):
        del mechfile[name]

    logger.debug("after removing name:{} mechfile:{}".format(name, mechfile))
    return save_mechfile(mechfile)


def save_mechfile(mechfile):
    """Save the mechfile object to a file called 'Mechfile'."""
    logger.debug('mechfile:{}'.format(mechfile))
    with open(os.path.join(main_dir(), 'Mechfile'), 'w+') as fp:
        json.dump(mechfile, fp, sort_keys=True, indent=2, separators=(',', ': '))
    return True


def locate(path, glob):
    """Locate a file in the path provided."""
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, glob):
                return os.path.abspath(os.path.join(root, filename))


def parse_vmx(path):
    """Parse the virtual machine configuration (.vmx) file."""
    vmx = collections.OrderedDict()
    with open(path) as fp:
        for line in fp:
            line = line.strip().split('=', 1)
            if len(line) > 1:
                vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def update_vmx(path, numvcpus=None, memsize=None):
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
        vmx["ethernet0.connectiontype"] = "nat"
        vmx["ethernet0.displayname"] = "Ethernet"
        vmx["ethernet0.linkstatepropagation.enable"] = "FALSE"
        vmx["ethernet0.pcislotnumber"] = "32"
        vmx["ethernet0.present"] = "TRUE"
        vmx["ethernet0.virtualdev"] = "e1000"
        vmx["ethernet0.wakeonpcktrcv"] = "FALSE"
        puts_err(colored.yellow("Added network interface to vmx file"))
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

    # puts_err(colored.yellow("Upgrading VM..."))
    # vmrun = VMrun(path)
    # vmrun.upgradevm()


def load_mechfile(should_exist=True):
    """Load the Mechfile from disk and return the object."""
    mechfile_fullpath = os.path.join(main_dir(), 'Mechfile')
    logger.debug("mechfile_fullpath:{}".format(mechfile_fullpath))
    if os.path.isfile(mechfile_fullpath):
        with open(mechfile_fullpath) as fp:
            try:
                mechfile = json.loads(uncomment(fp.read()))
                logger.debug('mechfile:{}'.format(mechfile))
                return mechfile
            except ValueError:
                puts_err(colored.red("Invalid Mechfile." + os.linesep))
    else:
        if should_exist:
            puts_err(colored.red(textwrap.fill(
                "Could not find a Mechfile in the current directory. "
                "A Mech environment is required to run this command. Run `mech init` "
                "to create a new Mech environment. Or specify the name of the VM you would "
                "like to start with `mech up <name>`. A final option is to change to a "
                "directory with a Mechfile and to try again."
            )))
            sys.exit(1)
        else:
            return {}


def build_mechfile_entry(location, box=None, name=None, box_version=None, requests_kwargs={}):
    """Build the Mechfile from the inputs."""
    logger.debug("location:{} name:{} box:{} box_version:{}".format(
                 location, name, box, box_version))
    mechfile_entry = {}
    if location is None:
        return mechfile_entry
    mechfile_entry['name'] = name
    if any(location.startswith(s) for s in ('https://', 'http://', 'ftp://')):
        mechfile_entry['url'] = location
        if not name:
            name = 'first'
        mechfile_entry['box'] = box
        if box_version:
            mechfile_entry['box_version'] = box_version
        return mechfile_entry
    elif location.startswith('file:') or os.path.isfile(re.sub(r'^file:(?://)?', '', location)):
        location = re.sub(r'^file:(?://)?', '', location)
        logger.debug('location:{}'.format(location))
        try:
            # see if the location is a json file
            with open(location) as fp:
                catalog = json.loads(uncomment(fp.read()))
        except Exception:
            mechfile_entry['file'] = location
        if not name:
            name = 'first'
        mechfile_entry['box'] = box
        if box_version:
            mechfile_entry['box_version'] = box_version
        logger.debug('mechfile_entry:{}'.format(mechfile_entry))
        return mechfile_entry
    else:
        try:
            account, box, v = (location.split('/', 2) + ['', ''])[:3]
            if not account or not box:
                puts_err(colored.red("Provided box name is not valid"))
            if v:
                box_version = v
            puts_err(
                colored.blue("Loading metadata for box '{}'{}".format(
                             location, " ({})".format(box_version) if box_version else "")))
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
    logger.debug("catalog:{} name:{} box_version:{}".format(catalog, name, box_version))
    return catalog_to_mechfile(catalog, name=name, box=box, box_version=box_version)


def catalog_to_mechfile(catalog, name=None, box=None, box_version=None):
    """Convert the Hashicorp cloud catalog entry to Mechfile entry."""
    logger.debug('catalog:{} name:{} box:{} box_version:{}'.format(catalog, name, box, box_version))
    mechfile = {}
    versions = catalog.get('versions', [])
    for v in versions:
        current_version = v['version']
        if not box_version or current_version == box_version:
            for provider in v['providers']:
                if 'vmware' in provider['name']:
                    mechfile['name'] = name
                    mechfile['box'] = catalog['name']
                    mechfile['box_version'] = current_version
                    mechfile['url'] = provider['url']
                    return mechfile
    puts_err(
        colored.red(
            "Couldn't find a VMWare compatible VM for '{}'{}".format(
                name, " ({})".format(box_version) if box_version else "")))
    sys.exit(1)


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
    stdoutdata, stderrdata = map(b2s, proc.communicate())
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
             instance_path=None, requests_kwargs={}, numvcpus=None,
             memsize=None):
    """Initialize the box. This includes uncompressing the files
       from the box file and updating the vmx file with
       desired settings.
    """
    logger.debug("name:{} box:{} box_version:{} location:{}".format(
                 name, box, box_version, location))
    if not locate(instance_path, '*.vmx'):
        name_version_box = add_box(
            name=name,
            box=box,
            box_version=box_version,
            location=location,
            force=force,
            save=save,
            requests_kwargs=requests_kwargs)
        if not name_version_box:
            puts_err(colored.red("Cannot find a valid box with a VMX file in it"))
            sys.exit(1)

        box_parts = box.split('/')
        box_dir = os.path.join(*filter(None, (mech_dir(), 'boxes',
                               box_parts[0], box_parts[1], box_version)))
        box_file = locate(box_dir, '*.box')

        puts_err(colored.blue("Extracting box '{}'...".format(box_file)))
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
                puts_err(colored.red("Cannot extract box"))
                sys.exit(1)
        else:
            tar = tarfile.open(box_file, 'r')
            tar.extractall(instance_path)

        if not save and box.startswith(tempfile.gettempdir()):
            os.unlink(box)

    vmx = locate(instance_path, '*.vmx')
    if not vmx:
        puts_err(colored.red("Cannot locate a VMX file"))
        sys.exit(1)

    update_vmx(vmx, numvcpus=numvcpus, memsize=memsize)
    return vmx


def add_box(name=None, box=None, box_version=None, location=None,
            force=False, save=True, requests_kwargs={}):
    """Add a box."""
    # build the dict
    logger.debug('name:{} box:{} box_version:{} location:{}'.format(
                 name, box, box_version, location))
    mechfile_entry = build_mechfile_entry(
        box=box,
        name=name,
        location=location,
        box_version=box_version,
        requests_kwargs=requests_kwargs)

    return add_mechfile(
        mechfile_entry,
        name=name,
        box=box,
        location=location,
        box_version=box_version,
        force=force,
        save=save,
        requests_kwargs=requests_kwargs)


def add_mechfile(mechfile_entry, name=None, box=None, box_version=None,
                 location=None, force=False, save=True, requests_kwargs={}):
    logger.debug('mechfile_entry:{} name:{} box:{} box_version:{} location:{}'.format(
                 mechfile_entry, name, box, box_version, location))

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
                           url=url, force=force, save=save,
                           requests_kwargs=requests_kwargs)
    puts_err(
        colored.red(
            "Could not find a VMWare compatible VM for '{}'{}".format(
                name, " ({})".format(box_version) if box_version else "")))


def add_box_url(name, box, box_version, url, force=False, save=True, requests_kwargs={}):
    """Add a box using the URL."""
    logger.debug('name:{} box:{} box_version:{} url:{}'.format(name, box, box_version, url))
    boxname = os.path.basename(url)
    box_parts = box.split('/')
    box_dir = os.path.join(*filter(None, (mech_dir(), 'boxes',
                           box_parts[0], box_parts[1], box_version)))
    exists = os.path.exists(box_dir)
    if not exists or force:
        if exists:
            puts_err(colored.blue("Attempting to download box '{}'...".format(box)))
        else:
            puts_err(colored.blue("Box '{}' could not be found. "
                     "Attempting to download...".format(box)))
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
            fp = tempfile.NamedTemporaryFile(delete=False)
            try:
                for chunk in progress_type(
                        r.iter_content(
                            chunk_size=1024),
                        label="{} ".format(boxname),
                        **progress_args):
                    if chunk:
                        fp.write(chunk)
                fp.close()
                if r.headers.get('content-type') == 'application/json':
                    # Downloaded URL might be a Vagrant catalog if it's json:
                    catalog = json.load(fp.name)
                    mechfile = catalog_to_mechfile(catalog, name, box, box_version)
                    return add_mechfile(
                        mechfile,
                        name=name,
                        box_version=box_version,
                        force=force,
                        save=save,
                        requests_kwargs=requests_kwargs)
                else:
                    # Otherwise it must be a valid box:
                    return add_box_file(box=box, box_version=box_version,
                                        filename=fp.name, url=url, force=force,
                                        save=save)
            finally:
                os.unlink(fp.name)
        except requests.HTTPError as exc:
            puts_err(colored.red("Bad response: %s" % exc))
            sys.exit(1)
        except requests.ConnectionError:
            puts_err(colored.red("Couldn't connect to '%s'" % url))
            sys.exit(1)
    return name, box_version, box


def add_box_file(box=None, box_version=None, filename=None, url=None, force=False, save=True):
    """Add a box using a file as the source. Returns box and box_version."""
    puts_err(colored.blue("Checking box '{}' integrity filename:{}...".format(box, filename)))

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
                puts_err(colored.red(textwrap.fill(
                    "This box is comprised of filenames starting with '/' or '..' "
                    "Exiting for the safety of your files."
                )))
                sys.exit(1)

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


def init_mechfile(location=None, box=None, name=None, box_version=None, requests_kwargs={}):
    """Initialize the Mechfile."""
    logger.debug("name:{} box:{} box_version:{} location:{}".format(
        name, box, box_version, location))
    mechfile_entry = build_mechfile_entry(
        location=location,
        box=box,
        name=name,
        box_version=box_version,
        requests_kwargs=requests_kwargs)
    logger.debug('mechfile_entry:{}'.format(mechfile_entry))
    return save_mechfile_entry(mechfile_entry, name, mechfile_should_exist=False)


def add_to_mechfile(location=None, box=None, name=None, box_version=None, requests_kwargs={}):
    """Add entry to the Mechfile."""
    logger.debug("name:{} box:{} box_version:{} location:{}".format(
        name, box, box_version, location))
    this_mech_entry = build_mechfile_entry(
        location=location,
        box=box,
        name=name,
        box_version=box_version,
        requests_kwargs=requests_kwargs)
    logger.debug('this_mech_entry:{}'.format(this_mech_entry))
    return save_mechfile_entry(this_mech_entry, name, mechfile_should_exist=False)


def get_requests_kwargs(arguments):
    """Get the requests key word arguments."""
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


def provision(instance, vmx, user, password, provision, show):
    """Provision an instance."""

    if instance == '':
        puts_err(colored.red("Need to provide an instance to provision()."))
        return

    if not vmx or not user or not password:
        puts_err(colored.red("Need provide vmx/user/password to provision()."))
        return

    puts_err(colored.green('Provisioning instance:{}'.format(instance)))

    vmrun = VMrun(vmx, user, password)
    # cannot run provisioning if vmware tools are not installed
    if not vmrun.installedTools():
        puts_err(colored.red("Cannot provision if VMware Tools are not installed."))
        return

    provisioned = 0
    if provision:
        for i, p in enumerate(provision):
            provision_type = p.get('type')
            if provision_type == 'file':
                source = p.get('source')
                destination = p.get('destination')
                if show:
                    puts_err(colored.green(" instance:{} provision_type:{} source:{} "
                             "destination:{}".format(instance, provision_type,
                                                     source, destination)))
                else:
                    if provision_file(vmrun, source, destination) is None:
                        puts_err(colored.red("Not Provisioned"))
                        return
                provisioned += 1

            elif provision_type == 'shell':
                inline = p.get('inline')
                path = p.get('path')

                args = p.get('args')
                if not isinstance(args, list):
                    args = [args]
                if show:
                    puts_err(colored.green(" instance:{} provision_type:{} inline:{} path:{} "
                             "args:{}".format(instance, provision_type, inline, path, args)))
                else:
                    if provision_shell(vmrun, inline, path, args) is None:
                        puts_err(colored.red("Not Provisioned"))
                        return
                provisioned += 1

            else:
                puts_err(colored.red("Not Provisioned ({}".format(i)))
                return
        else:
            puts_err(colored.green("VM ({}) Provision {} "
                     "entries".format(instance, provisioned)))
    else:
        puts_err(colored.blue("Nothing to provision"))


def provision_file(vm, source, destination):
    """Provision from file.
       This simply copies a file from host to guest.
    """
    puts_err(colored.blue("Copying ({}) to ({})".format(source, destination)))
    return vm.copyFileFromHostToGuest(source, destination)


def provision_shell(vm, inline, path, args=[]):
    """Provision from shell."""
    tmp_path = vm.createTempfileInGuest()
    logger.debug('inline:{} path:{} args:{} tmp_path:{}'.format(
                 inline, path, args, tmp_path))
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

            puts_err(colored.blue("Configuring script to run inline..."))
            fp = tempfile.NamedTemporaryFile(delete=False)
            try:
                fp.write(str.encode(inline))
                fp.close()
                if vm.copyFileFromHostToGuest(fp.name, tmp_path) is None:
                    return
            finally:
                os.unlink(fp.name)

        puts_err(colored.blue("Configuring environment..."))
        if vm.runScriptInGuest('/bin/sh', "chmod +x '{}'".format(tmp_path)) is None:
            return

        puts_err(colored.blue("Executing program..."))
        return vm.runProgramInGuest(tmp_path, args)

    finally:
        vm.deleteFileInGuest(tmp_path, quiet=True)


def config_ssh_string(config_ssh):
    """Build the ssh-config string."""
    ssh_config = "Host {}".format(config_ssh['Host']) + os.linesep
    for k, v in config_ssh.items():
        if k != 'Host':
            ssh_config += "  {} {}".format(k, v) + os.linesep
    return ssh_config
