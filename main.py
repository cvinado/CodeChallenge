#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Code challenge
This code progressively downloads Mygeotab vehicle data and store the most updated information in a CSV.
The CSV is created in the execution path

Example:
    Execute example:
        $ python main.py MyGdatabase

Options:
  -u, --user TEXT               MyGeotab username
  -p, --password TEXT           MyGeotab password
  --server TEXT                 The server (default is my.geotab.com)
  -i, --interval INTEGER RANGE  The data feed interval in seconds (default is
                                60 seconds)  [5<=x<=300]
  --help                        Shows help message.
"""

import click
from mygeotab import API
from datetime import datetime
from time import sleep
import csv
import os

# CSV fielnames
fieldnames = ['Date', 'Id', 'VIN', 'Coordinates', 'Odometer']
# CSV filename
filename = "ChristianChallenge_default.csv"
# Inizialitate CSV
i = 0
while os.path.exists(f"ChristianChallenge_{i}.csv"):
    i += 1
filename = f"ChristianChallenge_{i}.csv"
# Create File
newfile = open(filename, 'w', newline='')
writer = csv.DictWriter(newfile, fieldnames=fieldnames)
# Write down header line
writer.writeheader()
newfile.close()


def updatevehicle(api, vehicleId):
    with open(filename, 'a', newline='') as file:
        filewriter = csv.DictWriter(file, fieldnames=fieldnames)
        try:
            device = api.call('Get', typeName='Device', search=dict(id=vehicleId))[0]
            statusinfo = api.call('Get', typeName='DeviceStatusInfo', search=dict(deviceSearch=dict(id=device["id"]), diagnosticSearch=dict(id='DiagnosticOdometerId')))
            statusdata = api.call('Get', typeName='StatusData', search=dict(deviceSearch=dict(id=device["id"]), diagnosticSearch=dict(id='DiagnosticOdometerAdjustmentId'), fromdate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), todate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
            filewriter.writerow({'Date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Id': device["id"], 'VIN': device["vehicleIdentificationNumber"], 'Coordinates': {statusinfo[0]['latitude'], statusinfo[0]['longitude']}, 'Odometer': statusdata[0]['data']})
        except Exception:
            print("error while collecting a data input")
    file.close()


@click.command(help="A console data feeder example")
@click.argument("database", nargs=1, required=True)
@click.option("--user", "-u", prompt=True, help="MyGeotab username")
@click.option("--password", "-p", prompt=True, hide_input=True, help="MyGeotab password")
@click.option("--server", default=None, help="The server (default is my.geotab.com)")
@click.option(
    "--interval",
    "-i",
    type=click.IntRange(5, 300),
    default=60,
    help="The data feed interval in seconds (default is 60 seconds)",
)
def main(database, user=None, password=None, server=None, interval=60):
    # API authentication
    api = API(database=database, username=user, password=password, server=server)
    api.authenticate()
    devices = api.call('Get', typeName='Device')
    # Populate the CSV with the initial data
    for device in devices:
        updatevehicle(api, device["id"])

    while True:
        try:
            devices = api.call('Get', typeName='Device')
            # Populate the CSV with the initial data
            for device in devices:
                updatevehicle(api, device["id"])
        except (api.MyGeotabException, ConnectionError) as exception:
            print(exception)
        sleep(interval)


if __name__ == "__main__":
    main()
