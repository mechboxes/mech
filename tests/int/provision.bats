#!/usr/bin/env bats
#
# provision.bats - run provision tests
#
# Note: must be run from this directory
# like this: ./provision.bats

@test "provision testing" {
  cd provision

  # setup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  run mech up
  regex1="VM (first) started"
  regex2="VM (second) started"
  regex3="VM (third) started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  # show the provisioning
  run mech provision -s
  regex1="VM (first) Provision 2 entries"
  regex2="VM (second) Provision 3 entries"
  regex3="VM (third) Provision 0 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  # there should not be any files before file provisioning
  run mech ssh -c "ls -al /tmp/file1.txt" first
  regex1="No such file or directory"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # provision all
  run mech provision
  regex1="VM (first) Provision 2 entries"
  regex2="VM (second) Provision 3 entries"
  regex3="VM (third) Provision 0 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  # validate files were copied
  run mech ssh -c "ls -al /tmp/file1.txt" first
  regex1="vagrant"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # provision first (again)
  run mech provision first
  regex1="VM (first) Provision 2 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # provision second (again)
  run mech provision second
  regex1="VM (second) Provision 3 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # provision third (again)
  run mech provision third
  regex1="VM (third) Provision 0 entries"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
