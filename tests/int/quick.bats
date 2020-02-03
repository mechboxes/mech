#!/usr/bin/env bats
#
# quick.bats - run some quick tests
#
# Note: must be run from this directory
# like this: ./quick.bats

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
