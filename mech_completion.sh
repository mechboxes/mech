#!/usr/bin/env bash
#
# bash completion file for mech
#
# This script provides completion of:
#  - commands and their options
#
# To enable the completions either:
#  - place this file in /etc/bash_completion.d
#  or
#  - copy this file to e.g. ~/.mech-completion.sh and add the line
#    below to your .bashrc after bash completion features are loaded
#    . ~/.mech-completion.sh
#
_mech() {
  local cur prev opts base
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  #  Options that will complete
  opts="box destroy down global-status halt init ip list ls pause port provision ps reload resume scp snapshot stop ssh-config suspend up"

  #  Complete the arguments to some of the basic commands.
  case "${prev}" in
    box)
      COMPREPLY=( $( compgen -W 'add delete list ls remove' -- "$cur" ) )
      return 0
      ;;
    destroy)
      local commands="-f --force -h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    down)
      local commands="-f --force -h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    global-status)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
      return 0
      ;;
    init)
      local commands="--box --box-version --force -h --help --name"
      COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
      return 0
      ;;
    ip)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    list)
      local commands="-d --detail -h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    pause)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    port)
      local commands="--guest -h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    provision)
      local commands="-h --help -s --show"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    ps)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    reload)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    scp)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
      return 0
      ;;
    snapshot)
      COMPREPLY=( $( compgen -W 'delete list ls remove save' -- "$cur" ) )
      return 0
      ;;
    suspend)
      local commands="-h --help"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    up)
      local commands="--disable-provisioning --disable-shared-folders --gui -h --help --memsize --no-cache --no-nat --numvcpus"
      COMPREPLY=( $(compgen -W "${commands} $(get_instances)" -- ${cur}) )
      return 0
      ;;
    *)
      ;;
  esac

  COMPREPLY=($(compgen -W "${opts}" -- ${cur}))

}

get_instances () {
  echo $(mech list | awk '(NR > 1) { printf("%s ", $1) }')
}

complete -F _mech mech
# vim: ft=bash sw=2 ts=2 et
