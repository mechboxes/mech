# mech

I made this because I don't like VirtualBox and I wanted to use vagrant with VMWare Fusion but was too cheap to buy the Vagrant plugin.

https://blog.kchung.co/mech-vagrant-with-vmware-integration-for-free/

Usage is pretty straightforward:

```
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
```

`mech init` can be used to pull a box file which will be installed and generate a mechfile in the current directory. You can also pull boxes from Vagrant Cloud with `mech init bento/ubuntu-14.04`. Barring that, `mech up <name>` can also be used to specify a vmx file to start. 

# Install

`pip install git+https://github.com/ColdHeat/mech.git` for the lastest or `pip install mech` for what I last pushed to PyPi

# Shared Folders

If the box you init was created properly, you will be able to access the host's current working directory in `/mnt/hgfs/mech`. If you are having trouble try running: 

```bash
sudo apt-get install linux-headers-$(uname -r)
sudo vmware-config-tools.pl
```
