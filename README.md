# mech

I made this because I don't like VirtualBox and I wanted to use vagrant with VMWare Fusion but was too cheap to buy the Vagrant plugin.

https://blog.kchung.co/mech-vagrant-with-vmware-integration-for-free/

Usage is pretty straightforward:

```
Usage: mech [options] <command> [<args>...]

Options:
    -v, --version                    Print the version and exit.
    -h, --help                       Print this help.
    --debug                          Show debug messages.

Common commands:
    init              initializes a new mech environment by creating a mechfile
    destroy           stops and deletes all traces of the mech machine
    (up|start)        starts and provisions the mech environment
    (down|stop|halt)  stops the mech machine
    suspend           suspends the machine
    pause             pauses the mech machine
    ssh               connects to machine via SSH
    scp               copies files to and from the machine via SCP
    ip                outputs ip of the mech machine
    box               manages boxes: installation, removal, etc.
    (status|ps)       outputs status mech environments for this user
    provision         provisions the mech machine
    reload            restarts mech machine, loads new mechfile configuration
    resume            resume a paused/suspended mech machine
    snapshot          manages snapshots: saving, restoring, etc.
    port              displays information about guest port mappings
    push              deploys code in this environment to a configured destination

For help on any individual command run `mech <command> -h`

Example:

    Initialize and use a FreeBSD instance with a machine from HashiCorp's Vagrant Cloud:

        mech init freebsd/FreeBSD-11.1-RELEASE
        mech up
        mech ssh

    Initialize and use an Ubuntu instance with a machine from HashiCorp's Vagrant Cloud:
        mech init bento/ubuntu-14.04
        mech up
        mech ssh

```

`mech init` can be used to pull a box file which will be installed and generate a mechfile in the current directory. You can also pull boxes from Vagrant Cloud with `mech init freebsd/FreeBSD-11.1-RELEASE`. Barring that, `mech up <name>` can also be used to specify a vmx file to start.

# Install

`pip install git+https://github.com/mechboxes/mech.git`

# Shared Folders

If the box you init was created properly, you will be able to access the host's current working directory in `/mnt/hgfs/mech`. If you are having trouble try running:

```bash
sudo apt-get install linux-headers-$(uname -r)
sudo vmware-config-tools.pl
```
