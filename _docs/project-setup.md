---
title: Project Setup
permalink: /docs/project-setup/
---

The first step in configuring any Mech project is to create a Mechfile.
The purpose of the Mechfile is twofold:

1. Mark the root directory of your project. Many of the configuration options
   in Mech are relative to this root directory.

2. Describe the kind of machine and resources you need to run your project, as
   well as what software to install and how you want to access it.

Mech has a built-in command for initializing a directory for usage with Mech:
`mech init`. For the purpose of this getting started guide, please follow
along in your terminal:

```sh
~ $ mkdir mech_getting_started
~ $ cd mech_getting_started
~ $ mech init
```

This will place a Mechfile in your current directory. You can take a look at
the Mechfile if you want, it is filled with comments and examples. Do not be
afraid if it looks intimidating, we will modify it soon enough.

You can also run `mech init` in a pre-existing directory to set up Mech for
an existing project.

The Mechfile is meant to be committed to version control with your project,
if you use version control. This way, every person working with that project
can benefit from Mech without any upfront work.
