#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = 'mech 0.6'


def main():
    import os
    import sys

    from mech import Mech

    HOME = os.path.expanduser('~/.mech')
    if not os.path.exists(HOME):
        os.makedirs(HOME)

    arguments = Mech.docopt(Mech.__doc__, argv=sys.argv[1:], version=__version__)
    return Mech(arguments)()


if __name__ == "__main__":
    main()
