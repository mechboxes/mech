#!/usr/bin/env bats
#
# no_mechfile.bats - test without any Mechfile
#
# Note: must be run from this directory
# like this: ./no_mechfile.bats

@test "no Mechfile" {
  if ! [ -d no_mechfile ]; then
    mkdir no_mechfile
  fi
  cd no_mechfile

  run mech ls
  [ "$status" -eq 1 ]
  regex="Couldn't find a Mechfile"
  [[ "$output" =~ $regex ]]

  # cleanup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
  cd ..
}
