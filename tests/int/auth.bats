#!/usr/bin/env bats
#
# auth.bats - run some auth tests
#
# Note: must be run from this directory
# like this: ./auth.bats

@test "mech add-me/auth tests: up, test ssh command, and destroy" {
  if ! [ -d auth ]; then
    mkdir auth
  fi
  cd auth

  # setup
  # ensure there is no Mechfile first
  if [ -f Mechfile ]; then
    rm -f Mechfile
  fi
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  # Note: The '-a' is the 'add-me' option.
  run mech init -a bento/ubuntu-18.04
  regex1="Initializing"
  regex2="Loading metadata"
  regex3="has been initialized"
  regex4="mech up"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]
  [ -f Mechfile ]

  run mech list -d
  regex1="id_rsa.pub"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech up
  regex1="Loading metadata"
  regex2="could not be found"
  regex3="vmware_desktop"
  regex4="integrity filename"
  regex5=".vmx"
  regex6="Extracting"
  regex7="Added network"
  regex8="Bringing machine"
  regex9="Getting IP"
  regex10="Sharing folders"
  regex11="started"
  regex12="Added auth"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]
  [[ "$output" =~ $regex5 ]]
  [[ "$output" =~ $regex6 ]]
  [[ "$output" =~ $regex7 ]]
  [[ "$output" =~ $regex8 ]]
  [[ "$output" =~ $regex9 ]]
  [[ "$output" =~ $regex10 ]]
  [[ "$output" =~ $regex11 ]]
  [[ "$output" =~ $regex12 ]]

  # make sure we can re-run 'up'
  run mech up
  regex1="Bringing machine"
  regex2="Getting IP"
  regex3="Sharing folders"
  regex4="was already started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]

  # make sure we can run a command
  first_ip=`mech ip first`
  run ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=QUIET ${first_ip} -C uptime
  regex1="load average"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech add -a second bento/ubuntu-18.04
  regex1="Added to the Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech up second
  regex1="second"
  regex2="Added auth"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  rm Mechfile
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
