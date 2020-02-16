#!/usr/bin/env bats
#
# init_from_jsonfile.bats - init from a json file
#
# Note: must be run from this directory
# like this: ./init_from_jsonfile.bats

@test "mech init, up, destroy of ubuntu from json file" {
  cd init_from_jsonfile

  ubuntu='ubuntu-18.04'
  box_file="/tmp/${ubuntu}.box"
  # setup
  # ensure there is no Mechfile first
  if [ -f Mechfile ]; then
    rm -f Mechfile
  fi
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  # download the file if we don't have it already
  # that way we "cache" the file
  if ! [ -f "$box_file" ]; then
    wget -O "$box_file" "https://vagrantcloud.com/bento/boxes/${ubuntu}/versions/201912.04.0/providers/vmware_desktop.box"
  fi

  run mech init --box "bento/${ubuntu}" "file:bento_ubuntu_18-04.json"
  regex1="Initializing"
  regex2="has been initialized"
  regex3="mech up"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [ -f Mechfile ]

  run mech up
  regex1="Checking box"
  regex2="Extracting"
  regex3="Added network"
  regex4="Bringing machine"
  regex5="Getting IP"
  regex6="Sharing folders"
  regex7="started"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]
  [[ "$output" =~ $regex2 ]]
  [[ "$output" =~ $regex3 ]]
  [[ "$output" =~ $regex4 ]]
  [[ "$output" =~ $regex5 ]]
  [[ "$output" =~ $regex6 ]]
  [[ "$output" =~ $regex7 ]]

  run mech destroy -f
  regex1="Deleting"
  [ "$status" -eq 0 ]
  [[ "$output" =~ $regex1 ]]

  # clean up
  rm Mechfile || true
  find . -type d -name .mech -exec rm -rf {} \; 2> /dev/null || true

  cd ..
}
