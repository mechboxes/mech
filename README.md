# mech

![](https://github.com/mkinney/mech/workflows/Python%20packaage/badge.svg)

One of the authors made this because they don't like VirtualBox and wanted to use vagrant
with VMmare Fusion but was too cheap to buy the Vagrant plugin.

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
        destroy           stops and deletes all traces of the instances
        (up|start)        starts instances (aka virtual machines)
        (down|stop|halt)  stops the instances
        suspend           suspends the instances
        pause             pauses the instances
        ssh               connects to an instance via SSH
        ssh-config        outputs OpenSSH valid configuration to connect to the instances
        scp               copies files to/from the machine via SCP
        ip                outputs ip of an instance
        box               manages boxes: add, list remove, etc.
        global-status     outputs status of all virutal machines on this host
        status            outputs status of the instances
        ps                list running processes for an instance
        provision         provisions the Mech machine
        reload            restarts Mech machine, loads new Mechfile configuration
        resume            resume a paused/suspended Mech machine
        snapshot          manages snapshots: save, list, remove, etc.
        port              displays information about guest port mappings

For help on any individual command run `mech <command> -h`

Example:

    mech up --help

% mech up --help
Starts and provisions the mech environment.

Usage: mech up [options] [<instance>]

Options:
        --gui                        Start GUI
        --disable-shared-folder      Do not share folder with VM
        --provision                  Enable provisioning
        --insecure                   Do not validate SSL certificates
        --cacert FILE                CA certificate for SSL download
        --capath DIR                 CA certificate directory for SSL download
        --cert FILE                  A client SSL cert, if needed
        --checksum CHECKSUM          Checksum for the box
        --checksum-type TYPE         Checksum type (md5, sha1, sha256)
        --no-cache                   Do not save the downloaded box
        --memsize 1024               Specify the size of memory for VM
        --numvcpus 1                 Specify the number of vcpus for VM
    -h, --help                       Print this help


Example using mech:


Initializing and using a machine from HashiCorp's Vagrant Cloud:

    mech init bento/ubuntu-18.04
    mech up
    mech ssh
```

`mech init` can be used to pull a box file which will be installed and
generate a Mechfile in the current directory. You can also pull boxes
from Vagrant Cloud with `mech init freebsd/FreeBSD-11.1-RELEASE`.
Barring that, `mech up <name>` can also be used to specify a vmx file
to start.

# Install

`pip install -U mech`

or for the latest:

`pip install -U git+https://github.com/mechboxes/mech.git`

There are some open PRs that have yet to be merged. Until they are, you may consider
installing from:

`pip install -U git+https://github.com/mkinney/mech.git@multi-pr#egg=mech`

# Shared Folders

If the box you init was created properly, you will be able to access
the host's current working directory in `/mnt/hgfs/mech`. If you are
having trouble try running:

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

# Changing vcpus and/or memory size

If you do not specify how many vcpus or memory, then the values
in the .box file will be used. To override, use appropriate settings:

`mech up --numvcpus 2 --memsize 1024`


# Want zsh completion for commands/options (aka "tab completion")?
1. add these lines to ~/.zshrc

```bash
# folder of all of your autocomplete functions
fpath=($HOME/.zsh-completions $fpath)
# enable autocomplete function
autoload -U compinit
compinit
```

2. Copy script to something in fpath (Note: Run `echo $fpath` to show value.)

```bash
cp _mech ~/.zsh-completions/
```

3. Reload zsh

```bash
exec zsh
```

4. Try it out by typing `mech <tab>`. It should show the options available.

# Want bash completion for commands/options (aka "tab completion")?
1. add these lines to ~/.bash_profile

```bash
[ -f /usr/local/etc/bash_completion ] && . /usr/local/etc/bash_completion
```

2. Copy script to path above

```bash
cp mech_completion.sh /usr/local/etc/bash_completion/
```

3. Reload .bash_profile

```bash
source ~/.bash_profile
```

4. Try it out by typing `mech <tab>`. It should show the options available.
