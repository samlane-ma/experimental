#!/usr/bin/env python3

import json
import os

snaplist = ['ubuntu-budgie-welcome','core18','snapd']
snaps = []
arch = 'arm64'
name = 'stable'

print("Checking snap " + arch + "/" + name + " revisions:")
for snap in snaplist:
    os.system("curl -o snap.json -H 'Snap-Device-Series: 16' http://api.snapcraft.io/v2/snaps/info/" + snap + " > /dev/null 2>&1")
    with open("snap.json", "r") as file:
        key = file.read()
    os.remove('snap.json')
    y = json.loads(key)
    for j in y['channel-map']:
        if j['channel']['architecture'] == arch and j['channel']['name'] == name:
            snaps.append("Current {} {}/{} revision: {}_{}".format(snap,arch,name,snap,j['revision']))

for each in snaps:
    print(each)
