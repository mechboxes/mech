# mech

I made this because I don't like VirtualBox and I wanted to use vagrant with VMWare Fusion but was too cheap to buy the Vagrant plugin.

Usage is pretty straightforward:

```
Usage:
    mech init <url>
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech suspend [options]
    mech pause [options]
    mech ssh [options] [--user=<user>]
    mech ip [options]
    mech (list | status) [options]
    mech -h | --help
    mech --version
Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
```

`mech init` can be used to pull a box file which will be installed and generate a mechfile in the current directory. Barring that, `mech up <name>` can also be used to specify a vmx file to start. 

# Install

`pip install git+https://github.com/ColdHeat/mech.git` for the lastest or `pip install mech` for what I last pushed to PyPi
