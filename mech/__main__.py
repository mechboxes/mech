#!/usr/bin/env python
'''
mech.

Usage:
    mech init [<url>] [--name=<name>]
    mech rm [<name>]
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech suspend [options] [<name>]
    mech pause [options] [<name>]
    mech unpause [options] [<name>]
    mech ssh [options] [<name> --user=<user>]
    mech scp [options] [<name>] <src> <dst> [--user=<user>]
    mech ip [options] [<name>]
    mech (list | ls) [options]
    mech (status | ps) [options]
    mech -h | --help
    mech --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
'''
from __future__ import print_function

import os

from six import iteritems
from clint.textui import colored, puts

from . import utils
from .mech import Mech
from .docopt import docopt

HOME = os.path.expanduser("~/.mech")

def operation(op, name, options=None, kwargs=None, debug=False):
    if options is None:
        options = {}
    if name:
        vmx = utils.locate_vmx(name)
        if vmx:
            mechfile = utils.load_mechfile(name)
            m = Mech(debug=debug)
            m.vmx = vmx
            m.user = mechfile['user']
            for key, value in iteritems(options):
                setattr(m, key, value)
            method = getattr(m, op)
            if kwargs:
                method(**kwargs)
            else:
                method()
        else:
            puts(colored.red("Couldn't find a VMX in the specified directory"))
            return
    else:
        mechfile = utils.load_mechfile()
        if mechfile is None:
            puts(colored.red("Couldn't find a mechfile in the current directory any deeper directories"))
            puts(colored.red("You can specify the name of the VM you'd like to start with mech up <name>"))
            puts(colored.red("Or run mech init to setup a tarball of your VM or download the VM"))
            return
        vmx = mechfile.get('vmx')
        if vmx:
            m = Mech(debug=debug)
            m.vmx = vmx
            m.user = mechfile.get('user')
            for key, value in iteritems(options):
                setattr(m, key, value)
            method = getattr(m, op)
            if kwargs:
                method(**kwargs)
            else:
                method()
        else:
            puts(colored.red("Couldn't find a VMX in the mechfile"))
            return

def main(args=None):
    arguments = docopt(__doc__, version='mech 0.5')

    DEBUG = arguments['--debug']

    if not os.path.exists(HOME):
        os.makedirs(HOME)

    if arguments['init']:
        puts(colored.green("Initializing mech"))
        url = arguments['<url>']
        name = arguments['--name']
        Mech.setup(url, name)
        exit()

    elif arguments['list'] or arguments['ls']:
        Mech.list()
        exit()

    elif arguments['status'] or arguments['ps']:
        Mech.status(debug=DEBUG)
        exit()

    elif arguments['rm']:
        name = arguments['<name>']
        operation(op='remove', name=name, debug=DEBUG)
        exit()

    elif arguments['up'] or arguments['start']:
        name = arguments['<name>']
        gui = arguments['--gui']
        operation(op='start', name=name, options={'gui':gui}, debug=DEBUG)
        exit()

    elif arguments['down'] or arguments['stop']:
        name = arguments['<name>']
        operation(op='stop', name=name, debug=DEBUG)
        exit()

    elif arguments['pause']:
        name = arguments['<name>']
        operation(op='pause', name=name, debug=DEBUG)
        exit()

    elif arguments['unpause']:
        name = arguments['<name>']
        operation(op='unpause', name=name, debug=DEBUG)
        exit()

    elif arguments['suspend']:
        name = arguments['<name>']
        operation(op='suspend', name=name, debug=DEBUG)
        exit()

    elif arguments['ssh']:
        name = arguments['<name>']
        user = arguments.get("--user")
        if user:
            options = {'user':user}
        else:
            options = {}
        operation(op='ssh', name=name, options=options, debug=DEBUG)
        exit()

    elif arguments['scp']:
        name = arguments['<name>']
        user = arguments.get("--user")
        if user:
            options = {'user':user}
        else:
            options = {}
        src = arguments['<src>']
        dst = arguments['<dst>']
        operation(op='scp', name=name, options=options, kwargs={'src':src, 'dst':dst}, debug=DEBUG)
        exit()

    elif arguments['ip']:
        name = arguments['<name>']
        operation(op='ip', name=name, debug=DEBUG)
        exit()

if __name__ == "__main__":
    main()
