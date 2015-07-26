# hobo

I made this because I don't like VirtualBox and I wanted to use vagrant with VMWare Fusion but was too cheap to buy the Vagrant plugin. 

Usage is pretty straightforward:

```
Usage:
    hobo (up | start) [options] [<name> --gui]
    hobo (down | stop) [options] [<name>]
    hobo pause [options]
    hobo ssh [options]
    hobo ip [options]
    hobo (list | status) [options]
    hobo -h | --help
    hobo --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
```

You can simply be in the folder where the vmx is or specify the path to it. 

# Install

`pip install git+https://github.com/ColdHeat/hobo.git`
