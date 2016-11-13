#!/usr/bin/env python
'''
mech.

Usage:
    mech init [<url>] [--name=<name>]
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech suspend [options] [<name>]
    mech pause [options] [<name>]
    mech ssh [options] [<name> --user=<user>]
    mech scp <src> <dst> [--user=<user>]
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

from clint.textui import colored, puts
from clint.textui import progress
from clint.textui import prompt
from docopt import docopt
from mech import Mech
from pprint import pprint
import os
import utils

HOME = os.path.expanduser("~/.mech")

def operation(op, name, options=None):
    if options is None:
        options = {}
    if name:
        vmx = utils.locate_vmx(name)
        if vmx:
            mechfile = utils.load_mechfile(name)
            m = Mech()
            m.vmx = vmx
            m.user = mechfile['user']
            for key, value in options.iteritems():
                setattr(m, key, value)
            method = getattr(m, op)
            method()
        else:
            puts(colored.red("Couldn't find a VMX in the specified directory"))
    else:
        mechfile = utils.load_mechfile()
        vmx = mechfile.get('vmx')
        if vmx:
            m = Mech()
            m.vmx = vmx
            m.user = mechfile.get('user')
            for key, value in options.iteritems():
                setattr(m, key, value)
            method = getattr(m, op)
            method()
        else:
            puts(colored.red("Couldn't find a VMX in the mechfile"))

def main(args=None):
    arguments = docopt(__doc__, version='mech 0.3')

    DEBUG = arguments['--debug']

    if not os.path.exists(HOME):
        os.makedirs(HOME)

    if arguments['init']:
        puts(colored.green("Initializing mech"))
        mech_init(arguments['<url>'], arguments['--name'])
        exit()

    elif arguments['list'] or arguments['ls']:
        Mech.list()
        exit()

    elif arguments['status'] or arguments['ps']:
        Mech.status()
        exit()

    elif arguments['up'] or arguments['start']:
        name = arguments['<name>']
        gui = arguments['--gui']
        operation(op='start', name=name, options={'gui':gui})
        exit()

    elif arguments['down'] or arguments['stop']:
        name = arguments['<name>']
        operation(op='stop', name=name)
        exit()

    elif arguments['pause']:
        name = arguments['<name>']
        operation(op='pause', name=name)
        exit()

    elif arguments['suspend']:
        name = arguments['<name>']
        operation(op='suspend', name=name)
        exit()

    elif arguments['ssh']:
        name = arguments['<name>']
        user = arguments.get("--user")
        if user:
            options = {'user':user}
        else:
            options = {}
        operation(op='ssh', name=name, options=options)
        exit()

    elif arguments['scp']:
        name = arguments['<name>']
        name = arguments.get("--user")
        operation(op='scp', name=name, options={'user':user})
        exit()

    elif arguments['ip']:
        name = arguments['<name>']
        operation(op='ip', name=name, options={'user':user})
        exit()

if __name__ == "__main__":
    main()
