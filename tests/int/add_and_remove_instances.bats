#!/usr/bin/env bats
#
# shared_folders.bats - run shared_folders tests
#
# Note: must be run from this directory
# like this: ./shared_folders.bats

@test "add and remove instances tests" {
  if ! [ -d  add_and_remove_instances ]; then
     mkdir add_and_remove_instances
  fi
  cd add_and_remove_instances

  # setup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true
  if [ -f  Mechfile ]; then
     rm Mechfile
  fi

  run mech ls
  regex1="Could not find a Mechfile"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech remove one
  regex1="Could not find a Mechfile"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # check required params
  run mech add
  regex1="Usage: mech add "
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # check required params
  run mech add mrlesmithjr/alpine311
  regex1="Usage: mech add "
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # verify with add
  run mech add one mrlesmithjr/alpine311
  regex1="Added to the Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ls
  regex1=" one "
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # verify with init
  rm Mechfile
  run mech init mrlesmithjr/alpine311
  regex1="Added to the Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ls
  regex1=" one "
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # verify re-adding is not an issue
  run mech add one mrlesmithjr/alpine311
  regex1="Added to the Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # verify init with a Mechfile fails
  run mech init mrlesmithjr/alpine311
  regex1="already exists"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # add a 2nd instance
  run mech add two mrlesmithjr/alpine311
  regex1="Added to the Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ls
  regex1=" one "
  regex2=" two "
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  # remove one
  run mech remove one
  regex1="Removed"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ls
  regex1=" one "
  regex2=" two "
  [ "$status" -eq 0 ]
  ! [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  # try to remove one again
  run mech remove one
  regex1="There is no instance"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech remove two
  regex1="Removed"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ls
  regex1=" one "
  regex2=" two "
  [ "$status" -eq 0 ]
  ! [[ "$output" =~ $regex1 ]]
  ! [[ "$output" =~ $regex2 ]]

  # clean up
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
