# Find My PI (WIP)

Server method requires findmypi-server.py running on the PI

Mac method requires arp and nmap installed on the local machine

- findmypi.py:

  - running with "list" parameter returns list of PIs found on network
  - running with "server" parameter opens gui app to show PIs running the server app
  - running with "mac" parameter opens gui app to show PIs by searching mac address
  
- findmypi-server.py

  - starts the UDP server
  
- findmypiclient.py

  - module that contains the FindMyPI class, and the FindMyPITreeView class
