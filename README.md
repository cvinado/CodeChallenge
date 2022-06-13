# Code challenge

This code progressively downloads Mygeotab vehicle data and store the most updated information in a CSV.
The CSV is created in the execution path

##Example:
    Execute example:
    
    $ python main.py MyGdatabase

##Options:
  - -u, \--user TEXT               MyGeotab username
  - -p, \--password TEXT           MyGeotab password
  - \--server TEXT                 The server (default is my.geotab.com)
  - -i, \--interval INTEGER RANGE  The data feed interval in seconds (default is 60 seconds)  [5<=x<=300]
  - \--help                        Shows help message.
