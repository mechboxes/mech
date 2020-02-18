#!/usr/bin/env bats
#
# provision_using_me.bats - run provision tests using psk
#
# Note: must be run from this directory
# like this: ./provision_using_me.bats

@test "provision using psk testing" {
  cd provision_using_me

  # setup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
  mech destroy -f || true

  run mech up -r
  regex1="VM (first) started"
  regex2="VM (second) started"
  regex3="VM (third) started"
  regex4="Added auth"
  regex5="Removing username"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]
  [[ "$output" =~ $regex5 ]]

  # validate files were copied
  run mech ssh -c "ls -al /tmp/file1.txt" first
  regex1="vagrant"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # ensure that provision runs on 'mech up'
  run mech up
  regex1="VM (first) Provision 2 entries"
  regex2="VM (second) Provision 3 entries"
  regex3="VM (third) Provision 0 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
