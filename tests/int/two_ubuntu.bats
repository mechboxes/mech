#!/usr/bin/env bats
#
# two_ubuntu.bats - run some tests with multiple ubuntu instances
#
# Note: must be run from the tests/int directory
# like this: ./two_ubuntu.bats

@test "mech up/destroy of two ubuntu instances (first and second)" {
  cd two_ubuntu

  # setup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  run mech box ls
  [ "$status" -eq 0 ]

  run mech box list
  [ "$status" -eq 0 ]

  # ensure they can start the first time
  run mech up
  regex1="first"
  regex2="second"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  # ensure running 'up' again is not an issue
  run mech up
  regex1="first"
  regex2="second"
  regex3="already started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  run mech ls
  regex1="first"
  regex2="second"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  run mech status
  regex1="first"
  regex2="second"
  regex3="Tools running"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  run mech destroy -f
  regex1="first"
  regex2="second"
  regex3="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]

  run mech box list
  regex1="ubuntu"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech box remove bento/ubuntu-18.04
  regex1="Usage: mech box remove "
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech box remove bento/ubuntu-18.04 201912.04.0
  [ "$status" -eq 0 ]

  # make sure there is not ubuntu box
  run mech box list
  regex1="ubuntu"
  [ "$status" -eq 0 ]
  ! [[ "$output" =~ $regex1 ]]

  # clean up
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
