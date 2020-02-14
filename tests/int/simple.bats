#!/usr/bin/env bats
#
# simple.bats - run some simple tests
#
# Note: must be run from this directory
# like this: ./simple.bats

# Note: Using alpine because the image is the smallest I could find.
# This will download the box from internet.
@test "mech init, up, destroy of alpine" {
  if ! [ -d simple ]; then
    mkdir simple
  fi
  cd simple

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
  regex8="Bringing machine"
  regex9="Getting IP"
  regex10="Sharing folders"
  regex11="started"
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

  # make sure we can re-run 'up' with alias 'start'
  run mech start
  regex1="Bringing machine"
  regex2="Getting IP"
  regex3="Sharing folders"
  regex4="was already started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]

  # validate ps required arg
  run mech ps
  regex1="Usage: mech ps"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech ps first
  regex1="cmd=/sbin/init"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech status
  regex1="first"
  regex2="Tools running"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  run mech global-status
  regex1="simple/.mech/first/"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech list
  regex1="first"
  regex2="alpine"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  # validate alias works, too
  run mech ls
  regex1="first"
  regex2="alpine"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  run mech stop
  regex1="Stopped"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # try to stop a Stopped instance
  run mech stop
  regex1="Not stopped"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech start
  regex1="started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech pause
  regex1="Paused"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech resume
  regex1="resumed"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech suspend
  regex1="Suspended"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech resume
  regex1="started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # ssh: incomplete args
  run mech ssh
  regex1="Usage: mech ssh"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech ssh -c 'uptime' first
  regex1="load average"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # other form of command
  run mech ssh --command 'uptime' first
  regex1="load average"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # scp: incomplete args
  run mech scp
  regex1="Usage: mech scp"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  date > now
  run mech scp now first:/tmp
  regex1="100%"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  rm now

  run mech scp first:/tmp/now .
  regex1="100%"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  rm now

  # ip: incomplete args
  run mech ip
  regex1="Usage: mech ip"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech ip first
  regex1="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # ip: invalid arg
  run mech ip first2
  regex1="not found in the Mechfile"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech port
  regex1="Total port forwardings: 0"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech box list
  regex1="alpine"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # validate alias works, too
  run mech box list
  regex1="alpine"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  ## snapshots
  run mech snapshot list
  regex1="Total snapshots: 0"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # validate alias works, too
  run mech snapshot ls
  regex1="Total snapshots: 0"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are used
  run mech snapshot
  regex1="Usage: mech snapshot <subcommand>"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are used
  run mech snapshot save
  regex1="Usage: mech snapshot save"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are used
  run mech snapshot save snap1
  regex1="Usage: mech snapshot save"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech snapshot save snap1 first
  regex1="taken"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # re-run with same params, should err
  run mech snapshot save snap1 first
  regex1="A snapshot with the name already exists"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech snapshot ls
  regex1="Total snapshots: 1"
  regex2="snap1"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]

  # make sure params are used
  run mech snapshot delete
  regex1="Usage: mech snapshot delete"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are used (alias)
  run mech snapshot remove
  regex1="Usage: mech snapshot delete"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are used
  run mech snapshot delete snap1
  regex1="Usage: mech snapshot delete"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  # make sure params are valid
  run mech snapshot delete snap1 first1
  regex1="Usage: mech snapshot delete"
  [ "$status" -eq 1 ]
  [[ "$output" =~ $regex1 ]]

  run mech snapshot delete snap1 first
  regex1=" deleted"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  rm Mechfile
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
