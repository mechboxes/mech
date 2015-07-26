# mech

I made this because I don't like VirtualBox and I wanted to use vagrant with VMWare Fusion but was too cheap to buy the Vagrant plugin.

Usage is pretty straightforward:

```
Usage:
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech pause [options]
    mech ssh [options]
    mech ip [options]
    mech (list | status) [options]
    mech -h | --help
    mech --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
```

You can simply be in the folder where the vmx is or specify the path to it.

# Install

`pip install mech`
