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
    (list|ls)         lists all available boxes
    init              initializes a new Mech environment by creating a Mechfile
    destroy           stops and deletes all traces of the Mech machine
    (up|start)        starts and provisions the Mech environment
    (down|stop|halt)  stops the Mech machine
    suspend           suspends the machine
    pause             pauses the Mech machine
    ssh               connects to machine via SSH
    ssh-config        outputs OpenSSH valid configuration to connect to the machine
    scp               copies files to and from the machine via SCP
    ip                outputs ip of the Mech machine
    box               manages boxes: installation, removal, etc.
    global-status     outputs status Mech environments for this user
    status            outputs status of the Mech machine
    ps                list running processes in Guest OS
    provision         provisions the Mech machine
    reload            restarts Mech machine, loads new Mechfile configuration
    resume            resume a paused/suspended Mech machine
    snapshot          manages snapshots: saving, restoring, etc.
    port              displays information about guest port mappings
    push              deploys code in this environment to a configured destination

For help on any individual command run `mech <command> -h`

Example:

    Initializing and using a machine from HashiCorp's Vagrant Cloud:

        mech init bento/ubuntu-14.04
        mech up
        mech ssh
```

`mech init` can be used to pull a box file which will be installed and generate a Mechfile in the current directory. You can also pull boxes from Vagrant Cloud with `mech init freebsd/FreeBSD-11.1-RELEASE`. Barring that, `mech up <name>` can also be used to specify a vmx file to start.

# Install

`pip install -U git+https://github.com/mechboxes/mech.git@devel`

# Shared Folders

If the box you init was created properly, you will be able to access the host's current working directory in `/mnt/hgfs/mech`. If you are having trouble try running:

```bash
sudo apt-get update
sudo apt-get install linux-headers-$(uname -r) open-vm-tools
```

followed by

```bash
sudo vmware-config-tools.pl
```

or

```bash
vmhgfs-fuse .host:/mech /mnt/hgfs
```

