#!/usr/bin/env bats
#
# simple.bats - run some simple tests
#
# Note: must be run from this directory
# like this: ./simple.bats

@test "help" {
  run mech --help
  [ "$status" -eq 0 ]

  # cleanup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
}

@test "no args" {
  run mech
  [ "$status" -eq 1 ]
  [ "$output" = "Usage: mech [options] <command> [<args>...]" ]

  # cleanup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
}

@test "version" {
  run mech --version
  [ "$status" -eq 0 ]
  regex='mech v[0-9\.]+'
  [[ "$output" =~ $regex ]]

  # cleanup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
}

@test "no Mechfile" {
  cd no_mechfile

  run mech ls
  [ "$status" -eq 1 ]
  regex="Couldn't find a Mechfile"
  [[ "$output" =~ $regex ]]

  # cleanup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
  cd ..
}

# Note: Using alpine because the image is the smallest I could find.
# This will download the box from internet.
@test "mech init, up, destroy of alpine" {
  cd init_mechfile

  # setup
  # ensure there is no Mechfile first
  if [ -f Mechfile ]; then
    rm -f Mechfile
  fi
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  run mech init
  [ "$status" -eq 1 ]
  regex="Usage: mech init "
  [[ "$output" =~ $regex ]]

  run mech init mrlesmithjr/alpine311
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

  run mech up
  regex1="Loading metadata"
  regex2="could not be found"
  regex3="vmware_desktop"
  regex4="integrity filename"
  regex5=".vmx"
  regex6="Extracting"
  regex7="Added network"
  regex8="Bringing machine up"
  regex9="Getting IP"
  regex10="Sharing current folder"
  regex11="VM started"
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

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  rm Mechfile
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
