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
from mygeotab.ext import feed
from tempfile import NamedTemporaryFile
from datetime import datetime
import shutil
import csv

# CSV name
filename = 'ChristianChallenge.csv'

# CSV fielnames
fieldnames = ['Id', 'VIN', 'Coordinates', 'Odometer']


# Class for the "Device" feed
class DeviceListener(feed.DataFeedListener):
    def __init__(self, api):
        self.api = api
        super(feed.DataFeedListener, self).__init__()

    def on_data(self, data):
        for device in data:
            updateCSV(device['id'], "VIN", device["vehicleIdentificationNumber"])
            print("DeviceListener")

    def on_error(self, error):
        click.secho(error, fg="red")
        return True


# Class for the "DeviceStatusInfo" feed
class DeviceStatusListener(feed.DataFeedListener):
    def __init__(self, api):
        self.api = api
        super(feed.DataFeedListener, self).__init__()

    def on_data(self, data):
        for device in data:
            updateCSV(device['device']['id'], "Coordinates", "{" + str(device['latitude']) + "," + str(device['longitude']) + "}")
            print("DeviceStatusListener")

    def on_error(self, error):
        click.secho(error, fg="red")
        return True


# Class for the "StatusData" feed
class StatusDataListener(feed.DataFeedListener):
    def __init__(self, api):
        self.api = api
        super(feed.DataFeedListener, self).__init__()

    def on_data(self, data):
        for device in data:
            if device["data"] > 0:
                updateCSV(device['device']['id'], "Odometer", device["data"])
                print("StatusDataListener")

    def on_error(self, error):
        click.secho(error, fg="red")
        return True


# CSV initialization function
def initializeCSV(api):
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        devices = api.call('Get', typeName='Device')
        for device in devices:
            statusinfo = api.call('Get', typeName='DeviceStatusInfo', search=dict(deviceSearch=dict(id=device["id"]), diagnosticSearch=dict(id='DiagnosticOdometerId')))
            statusdata = api.call('Get', typeName='StatusData', search=dict(deviceSearch=dict(id=device["id"]), diagnosticSearch=dict(id='DiagnosticOdometerAdjustmentId'), fromdate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), todate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
            writer.writerow({'Id': device["id"], 'VIN': device["vehicleIdentificationNumber"], 'Coordinates': {statusinfo[0]['latitude'], statusinfo[0]['longitude']}, 'Odometer': statusdata[0]['data']})


# CSV update function
def updateCSV(identification, field, value):
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    with open(filename, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        writer = csv.DictWriter(tempfile, fieldnames=fieldnames)
        for row in reader:
            row = {'Id': row['Id'], 'VIN': row['VIN'], 'Coordinates': row['Coordinates'], 'Odometer': row['Odometer']}
            if row['Id'] == str(identification):
                print('updating row', row['Id'])
                row[field] = value
            writer.writerow(row)
    shutil.move(tempfile.name, filename)


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
    # Create the CSV with the initial data
    initializeCSV(api)
    # Create the datafeeds for the different information
    feed.DataFeed(api, DeviceListener(api), "Device", interval=interval).start()
    feed.DataFeed(api, DeviceStatusListener(api), "DeviceStatusInfo", interval=interval).start()
    feed.DataFeed(api, StatusDataListener(api), "StatusData", interval=interval, search=dict(diagnosticSearch=dict(id='DiagnosticOdometerAdjustmentId'), fromdate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), todate=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))).start()


if __name__ == "__main__":
    main()