---
title: Installation
permalink: /docs/installation/
---

Getting {{ site.name }} installed and ready-to-go should only take a few minutes.
If it ever becomes a pain, please [file an issue]({{ site.repository }}/issues/new)
(or submit a pull request) describing the issue you encountered and how
we might make the process easier.


Mech requires Python 2 or Python 3 to work, the easiest way to install it would
be to use pip install:


## PyPI

It can be installed by using the following command:

```sh
~ $ pip install mech
```


## Verifying the Installation

After installing Mech, verify the installation worked by opening a new command
prompt or console, and checking that mech is available:

```sh
~ $ mech --help
Usage: mech [options] <command> [<args>...]

Options:
    -v, --version                    Print the version and exit.
    -h, --help                       Print this help.
    --debug                          Show debug messages.
# ...
```
