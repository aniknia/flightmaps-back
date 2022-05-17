import numpy as np
import math as ma
import pandas as pd
from PIL import Image
import os
import json

path = os.path.abspath(os.path.dirname(__file__))


def airport_search(airport_code):
    reload = True

    # Import airport data
    if reload:
        airport_file = os.path.join(path, "airports.csv")
        airports = pd.read_csv(airport_file)
    # Grabs latitude and longitude of airport
    airport_code = airport_code.upper()
    if len(airport_code) == 3:
        try:
            entry = airports.loc[airports["IATA"].isin([airport_code])]
            lat = float(entry["Latitude"])
            long = float(entry["Longitude"])
        except:
            return False
    else:
        try:
            entry = airports.loc[airports["ICAO"].isin([airport_code])]
            lat = float(entry["Latitude"])
            long = float(entry["Longitude"])
        except:
            return False
    return lat, long


def great_circle(start, stop):
    # Grabbing coordinate pairs
    lat1, long1 = start[0], start[1]
    lat2, long2 = stop[0], stop[1]

    f = np.linspace(0, 1, 1000)

    d = np.arccos(
        np.sin(np.radians(lat1)) * np.sin(np.radians(lat2))
        + np.cos(np.radians(lat1))
        * np.cos(np.radians(lat2))
        * np.cos(np.radians(long1 - long2))
    )
    A = np.sin(np.radians((1 - f) * d)) / np.sin(np.radians(d))
    B = np.sin(np.radians(f * d)) / np.sin(np.radians(d))

    x = A * np.cos(np.radians(lat1)) * np.cos(np.radians(long1)) + B * np.cos(
        np.radians(lat2)
    ) * np.cos(np.radians(long2))
    y = A * np.cos(np.radians(lat1)) * np.sin(np.radians(long1)) + B * np.cos(
        np.radians(lat2)
    ) * np.sin(np.radians(long2))
    z = A * np.sin(np.radians(lat1)) + B * np.sin(np.radians(lat2))

    traj_lat = np.arctan2(z, np.sqrt(np.power(x, 2) + np.power(y, 2)))
    traj_long = np.arctan2(y, x)

    temp = {"Latitude": traj_lat, "Longitude": traj_long}
    trajraw = pd.DataFrame(data=temp)

    return trajraw, d


def kavraiskiy_vii(trajkrav):
    # Outputs (x,y) position of a [latitude,longitude] pair expressed in
    # degrees. x and y are scaled to unit values.

    # Converting points to kavraiskiy points
    trajkrav["Longitude"] = trajkrav.apply(
        lambda x: (
            (3 * x["Longitude"] / 2)
            * np.sqrt((1 / 3) - np.power((x["Latitude"] / np.pi), 2))
            * (2 / (np.sqrt(3) * np.pi))
        ),
        axis=1,
    )

    # TODO: check which is faster
    # latlong['Latitude'] = (-1) * latlong['Latitude'] / (np.pi / 2)
    trajkrav["Latitude"] = trajkrav["Latitude"].map(lambda x: (-1) * x / (np.pi / 2))

    return trajkrav


def scaler(trajxy):
    # File paths
    map_file = os.path.join(path, "kavraiskiy_vii_dark.jpg")

    # Opening map
    try:
        world_map = Image.open(map_file)
    except IOError:
        print("Image not found...")
        pass
    world_map = Image.open(map_file)

    # Map Limits
    height, width = world_map.size
    west = [5, 592]
    east = [2045, 592]
    north = [1025, 3]
    south = [1025, 1181]
    maplims = [west[0], east[0], north[1], south[1]]

    # Setting up variables
    trajsc = pd.DataFrame([], columns=["Latitude", "Longitude"])

    # Finding map bounds
    width = (maplims[1] - maplims[0]) / 2
    height = (maplims[3] - maplims[2]) / 2

    zerolong = maplims[0] + width
    zerolat = maplims[2] + height

    # Edge of map coefficients
    a = 0.001332
    b = -1.602
    c = 495
    d = 0

    # Scaling points to world map
    trajsc["Latitude"] = trajxy["Latitude"].map(
        lambda x: zerolat + (height * x), na_action="ignore"
    )

    trajsc["Longitude"] = trajxy["Longitude"].map(
        lambda x: zerolong + (width * x), na_action="ignore"
    )

    return trajsc


def main(route):
    start = airport_search(route[0])
    end = airport_search(route[1])
    if start and end:
        # trajectory in degrees lat/long
        trajraw, distance = great_circle(start, end)

        # trajectory in x/y (scaled to unit values)
        trajxy = kavraiskiy_vii(trajraw)

        # trajectory in pixels (scaled to map limits)
        trajsc = scaler(trajxy)

        distance *= 6365

        time = distance / 920

        carbon = time * 92

        json = {}
        json["x"] = trajsc["Longitude"].to_list()
        json["y"] = trajsc["Latitude"].to_list()
        json["distance"] = distance
        json["time"] = time
        json["carbon"] = carbon

        return json
    else:
        return False
