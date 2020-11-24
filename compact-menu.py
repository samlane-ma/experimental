#!/usr/bin/env python3

import gi.repository
from gi.repository import Gio
import subprocess, sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1].upper() in ["TRUE","ON"]:
            compact = True
        elif sys.argv[1].upper() in ["FALSE","OFF"]:
            compact = False
        else:
            print ("expected argument: true | false")
            exit(1)
    else:
        print ("expected argument: true | false")
        exit(1)

    process = subprocess.Popen(["dconf dump '/com/solus-project/budgie-panel/applets/'"
                                + "| grep -B 3 'Budgie Menu' | awk -F'[' '{print $2}'" 
                                + "| awk -F']' '{print $1}' | grep '{'"], shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    key = out.decode("UTF-8")[:-1]
    if key != "":
        print("Found key: {}. Setting to {}.".format(key,compact))
        menu_setting = Gio.Settings.new_with_path("com.solus-project.budgie-menu", 
                                         "/com/solus-project/budgie-panel/instance/budgie-menu/"
                                         + key +"/")
        menu_setting.set_boolean("menu-compact", compact)
    else:
        print ("Error changing setting. Budgie Menu possibly not installed.")
        exit(1)

