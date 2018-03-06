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

import os
import sys
import logging

from mech import Mech
from docopt import docopt


HOME = os.path.expanduser('~/.mech')


def main(args=None):
    arguments = docopt(__doc__, version='mech 0.6')
    # print(arguments)

    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if arguments['--debug']:
        logger.setLevel(logging.DEBUG)

    if not os.path.exists(HOME):
        os.makedirs(HOME)

    mech = Mech()

    if arguments['box']:

        if arguments['list'] or arguments['ls']:
            return mech.box_list()

        if arguments['add']:
            name = arguments['<name>']
            url = arguments['<url>'] or arguments['<path>']
            version = arguments.get('<VERSION>')
            return mech.box_add(name, url, version=version)

    if arguments['init']:
        name = arguments['<name>']
        url = arguments['<url>'] or arguments['<path>']
        version = arguments.get('<VERSION>')
        force = arguments['-f'] or arguments['--force']
        return mech.init(name, url, version=version, force=force)

    if arguments['status'] or arguments['ps']:
        return mech.status()

    if arguments['destroy']:
        force = arguments['-f'] or arguments['--force']
        return mech.destroy(force=force)

    if arguments['up'] or arguments['start']:
        return mech.start(gui=arguments['--gui'])

    if arguments['down'] or arguments['stop']:
        return mech.stop()

    if arguments['pause']:
        return mech.pause()

    if arguments['suspend']:
        return mech.suspend()

    if arguments['ssh']:
        user = arguments.get('--user')
        return mech.ssh(user=user)

    if arguments['scp']:
        src = arguments['<src>']
        dst = arguments['<dst>']
        user = arguments.get('--user')
        return mech.scp(src, dst, user=user)

    if arguments['ip']:
        return mech.ip()


if __name__ == "__main__":
    main()
