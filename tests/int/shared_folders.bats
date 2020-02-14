#!/usr/bin/env bats
#
# shared_folders.bats - run shared_folders tests
#
# Note: must be run from this directory
# like this: ./shared_folders.bats

@test "shared folders testing" {
  cd shared_folders

  # setup
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  run mech up
  regex1="VM (first) started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first
  regex1="Mechfile"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # make sure we can see files on 2nd "mech2" mount
  date > /tmp/now
  run mech ssh -c "ls -al /mnt/hgfs/mech2/now" first
  regex1=" /mnt/hgfs/mech2/now"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  rm /tmp/now

  run mech stop
  regex1="Stopped"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech up --disable-shared-folders
  regex1="VM (first) started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first
  regex1="No such file or directory"
  [ "$status" -eq 2 ]
  [[ "$output" =~ $regex1 ]]

  run mech pause
  regex1="Paused"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech resume --disable-shared-folders
  regex1="VM (first) started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first
  regex1="No such file or directory"
  [ "$status" -eq 2 ]
  [[ "$output" =~ $regex1 ]]

  run mech pause
  regex1="Paused"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech resume
  regex1="VM (first) started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech ssh -c "ls -al /mnt/hgfs/mech/Mechfile" first
  regex1="Mechfile"
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
