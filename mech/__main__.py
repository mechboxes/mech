#!/usr/bin/env python
'''
mech.

Usage:
    mech init <name> [<url>|<path>] [--box-version=<VERSION>] [-f | --force]
    mech destroy
    mech (up | start) [options] [--gui]
    mech (down | stop) [options]
    mech suspend [options]
    mech pause [options]
    mech ssh [options] [--user=<user>]
    mech scp <src> <dst> [--user=<user>]
    mech ip [options]
    mech box add (<name>|<url>|<path>) [--box-version=<VERSION>]
    mech box (list | ls) [options]
    mech (status | ps) [options]
    mech -h | --help
    mech --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
'''

from clint.textui import colored, puts
from docopt import docopt
from mech import Mech
import os
import utils

HOME = os.path.expanduser('~/.mech')


def operation(op, options=None, kwargs=None):
    if options is None:
        options = {}
    mechfile = utils.load_mechfile()
    if mechfile is None:
        puts(colored.red("Couldn't find a mechfile in the current directory any deeper directories"))
        puts(colored.red("You can specify the name of the VM you'd like to start with mech up <name>"))
        puts(colored.red("Or run mech init to setup a tarball of your VM or download the VM"))
        return
    vmx = mechfile.get('vmx')
    if vmx:
        m = Mech()
        m.vmx = vmx
        m.user = mechfile.get('user')
        for key, value in options.iteritems():
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
    arguments = docopt(__doc__, version='mech 0.6')
    # print(arguments)

    # DEBUG = arguments['--debug']

    if not os.path.exists(HOME):
        os.makedirs(HOME)

    if arguments['init']:
        puts(colored.green("Initializing mech"))
        name = arguments['<name>']
        url = arguments['<url>'] or arguments['<path>']
        version = arguments.get('<VERSION>')
        Mech.init(name, url, version, arguments['-f'] or arguments['--force'])
        exit()

    elif arguments['box']:
        if arguments['list'] or arguments['ls']:
            Mech.list()
            exit()
        elif arguments['add']:
            name = arguments['<name>']
            url = arguments['<url>'] or arguments['<path>']
            version = arguments.get('<VERSION>')
            Mech.add(name, url, version)
            exit()

    elif arguments['status'] or arguments['ps']:
        Mech.status()
        exit()

    elif arguments['destroy']:
        force = arguments['-f'] or arguments['--force']
        operation(op='destroy', options={'force': force})
        exit()

    elif arguments['up'] or arguments['start']:
        gui = arguments['--gui']
        operation(op='start', options={'gui': gui})
        exit()

    elif arguments['down'] or arguments['stop']:
        operation(op='stop')
        exit()

    elif arguments['pause']:
        operation(op='pause')
        exit()

    elif arguments['suspend']:
        operation(op='suspend')
        exit()

    elif arguments['ssh']:
        user = arguments.get('--user')
        if user:
            options = {'user': user}
        else:
            options = {}
        operation(op='ssh', options=options)
        exit()

    elif arguments['scp']:
        user = arguments.get('--user')
        if user:
            options = {'user': user}
        else:
            options = {}
        src = arguments['<src>']
        dst = arguments['<dst>']
        operation(op='scp', options=options, kwargs={'src': src, 'dst': dst})
        exit()

    elif arguments['ip']:
        operation(op='ip')
        exit()


if __name__ == "__main__":
    main()
