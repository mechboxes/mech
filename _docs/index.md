---
title: Welcome
permalink: /docs/home/
redirect_from: /docs/index.html
---

## What is Mech?

Mech is a tool for building and managing virtual machine environments in a
single workflow. With an easy-to-use workflow and focus on automation, Mech
lowers development environment setup time, increases production parity, and
makes the "works on my machine" excuse a relic of the past.

We made mech because we don't like VirtualBox and we wanted to use Vagrant with
VMWare Fusion but either it was too expensive or we were too cheap to buy the
Vagrant plugin.

If you are already familiar with the basics of Mech, the documentation provides
a better reference build for all available features and internals.


## Why Mech?

Mech provides easy to configure, reproducible, and portable work environments
built on top of industry-standard technology and controlled by a single
consistent workflow to help maximize the productivity and flexibility of you
and your team.

To achieve its magic, Mech stands on the shoulders of giants. Machines are
provisioned on top of VMware. Then, industry-standard provisioning tools such
as shell scripts, can automatically install and configure software on the
virtual machine.


```sh
~ $ mech --help
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

---

If you come across anything along the way that we haven't covered, or if you
know of a tip you think others would find handy, please [file an
issue]({{ site.repository }}/issues/new) and we'll see about
including it in this guide.
