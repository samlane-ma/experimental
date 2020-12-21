#!/usr/bin/env python3

import json
import os
import sys

snaplist = ['core18','snapd','ubuntu-budgie-welcome']
snap_revs = []
arch = 'arm64'
name = 'stable'

if len(sys.argv) > 1:
    seedfile = sys.argv[1]
else:
    seedfile = "seed.yaml"

print("Checking snap {}/{} revisions".format(arch,name))
for snap in snaplist:
    revision = "unavailable"
    os.system("curl -o snap.json -H 'Snap-Device-Series: 16' http://api.snapcraft.io/v2/snaps/info/" + snap + " > /dev/null 2>&1")
    with open("snap.json", "r") as file:
        key = file.read()
    os.remove('snap.json')
    y = json.loads(key)
    for j in y['channel-map']:
        if j['channel']['architecture'] == arch and j['channel']['name'] == name:
            revision = "{}_{}".format(snap,j['revision'])
    snap_revs.append(revision)

for i in range(len(snaplist)):
    print("Current {} {}/{} revision: {}".format(snaplist[i],arch,name,snap_revs[i]))
    if not snap_revs[i] == "unavailable":
        os.system("sed -i '/{}_/c\    file: {}.snap' {}".format(snaplist[i],snap_revs[i],seedfile))
print("Updated " + seedfile)
