import numpy as np
import math as ma
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image
import json
import base64
import io
import os

path = os.path.abspath(os.path.dirname(__file__))

# TODO: modify code for individual requests instead of batches
# TODO: remove useless comments, code should speak for itself


class Action:
    def __init__(self):
        # File paths
        self.map_file = os.path.join(path, "kavraiskiy_vii_dark.jpg")
        output_path = ""

        # Flags
        reload = True
        saveout = True

        # Opening map
        try:
            world_map = Image.open(self.map_file)
        except IOError:
            print("Image not found...")
            pass
        world_map = Image.open(self.map_file)

        # Map Limits
        height, width = world_map.size
        west = [5, 592]
        east = [2045, 592]
        north = [1025, 3]
        south = [1025, 1181]
        self.maplims = [west[0], east[0], north[1], south[1]]

        # Plot settings
        self.trajectory_density = 1000
        self.past_symbol = "r."
        self.future_symbol = "c."
        self.trajectory_marker_size = 0.5
        self.city_symbol = "x"
        self.city_color = "y"
        self.city_size = 2
        self.future_index = 11

        # Save settings
        self.img_size = 2000

        # Import airport data
        if reload:
            airport_file = os.path.join(path, "airports.csv")
            self.airports = pd.read_csv(airport_file)

        # Array of coordinates
        self.coordinates = []
        self.json_obj = {}

        # For debugging
        pd.set_option("display.max_rows", 10)

    def airport_search(self, airport_code):
        # Grabs latitude and longitude of airport
        airport_code = airport_code.upper()
        if len(airport_code) == 3:
            try:
                entry = self.airports.loc[self.airports["IATA"].isin([airport_code])]
                lat = float(entry["Latitude"])
                long = float(entry["Longitude"])
            except:
                return False
        else:
            try:
                entry = self.airports.loc[self.airports["ICAO"].isin([airport_code])]
                lat = float(entry["Latitude"])
                long = float(entry["Longitude"])
            except:
                return False
        return lat, long

    def great_circle(self, start, stop):
        # Grabbing coordinate pairs
        lat1, long1 = start[0], start[1]
        lat2, long2 = stop[0], stop[1]

        f = np.linspace(0, 1, self.trajectory_density)

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

        trajraw = pd.DataFrame(traj_lat, columns=["Latitude"])
        trajraw["Longitude"] = traj_long

        return trajraw

    def kavraiskiy_vii(self, trajkrav):
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
        trajkrav["Latitude"] = trajkrav["Latitude"].map(
            lambda x: (-1) * x / (np.pi / 2)
        )

        return trajkrav

    def scaler(self, trajxy):
        # Setting up variables
        trajsc = pd.DataFrame([], columns=["Latitude", "Longitude"])

        # Finding map bounds
        width = (self.maplims[1] - self.maplims[0]) / 2
        height = (self.maplims[3] - self.maplims[2]) / 2

        zerolong = self.maplims[0] + width
        zerolat = self.maplims[2] + height

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

    def gc_kav_traj(self, start, stop):
        # Returns great circle trajectory connecting two points.
        # Trajectory is projected for Kavraiskiy VII map.
        # Inputs:
        #   - start, stop: each a [lat,long] pair, in deg
        #   - n: number of points in trajectory
        #   - maplims: [west,east,north,south]: pixel ordinate for each limit of
        #               the map (x-ordinate for west/east, y-ordinate for
        #               north/south)
        #
        # Outputs:
        #   - trajsc: a matrix of format [x1, ... , xn ; y1, ... , yn] of pixel
        #           coordinates for the great circle, scaled to the Kav. VII map.

        # trajectory in degrees lat/long
        trajraw = self.great_circle(start, stop)

        # trajectory in x/y (scaled to unit values)
        trajxy = self.kavraiskiy_vii(trajraw)

        # trajectory in pixels (scaled to map limits)
        trajsc = self.scaler(trajxy)

        return trajsc

    # locations=[['LAX', 'NRT'], ['LAX', 'EDHE'], ['EDHE', 'LEN'], ['LEN', 'LAX']]

    def logger(self, data):
        f = open(os.path.join(path, "demofile1.txt"), "a")
        f.write("\n New Data Set")
        for i in range(1, len(data[0]), 2):
            f.write("\n From: " + str(data[0][i - 1]) + " To: " + str(data[0][i]))
        f.close()

    def format_data(self, data):
        self.locations = []
        for item in data:
            self.locations.append([str(item[0]).upper(), str(item[1]).upper()])

    def format_json(self, data):
        # INPUT: json from site frontend
        # OUTPUT: list of locations
        return 0

    def draw_map(self):
        # Draw underlying map
        world_map_plot = plt.imread(self.map_file)
        fig, ax = plt.subplots()
        ax.imshow(world_map_plot)
        plt.gca().set_axis_off()

        for row in self.Locations:
            # Grab start and end locations
            route_start, route_end = row[0], row[1]

            if route_start != "" or route_end != "":

                # Find starting and ending corrdinates
                start_pos = self.airport_search(route_start)
                if start_pos == False:
                    continue
                end_pos = self.airport_search(route_end)
                if end_pos == False:
                    continue

                # Convert coordinates to kavraiskiy vii coordinates
                coordinates = self.gc_kav_traj(start_pos, end_pos)

                # Plot path between locations
                plt.plot(
                    coordinates["Longitude"],
                    coordinates["Latitude"],
                    "r",
                    linewidth=self.trajectory_marker_size,
                )

                # Plot start and end locations
                plt.plot(
                    coordinates["Longitude"][0],
                    coordinates["Latitude"][0],
                    self.city_symbol,
                    color=self.city_color,
                    markersize=self.city_size,
                )
                plt.plot(
                    coordinates["Longitude"][self.trajectory_density - 1],
                    coordinates["Latitude"][self.trajectory_density - 1],
                    self.city_symbol,
                    color=self.city_color,
                    markersize=self.city_size,
                )
        plt.savefig(
            os.path.join(path, "kavraiskiy_vii_wallpaper.jpg"),
            bbox_inches="tight",
            pad_inches=0,
            dpi=self.img_size,
        )

    def get_coords(self):
        for row in self.locations:
            # Grab start and end locations
            route_start, route_end = row[0], row[1]

            if route_start != "" or route_end != "":

                # Find starting and ending corrdinates
                start_pos = self.airport_search(route_start)
                if start_pos == np.nan:
                    continue
                end_pos = self.airport_search(route_end)
                if end_pos == np.nan:
                    continue

                # Convert coordinates to kavraiskiy vii coordinates
                self.coordinates.append(self.gc_kav_traj(start_pos, end_pos))

    def pass_img(self):
        im = Image.open(os.path.join(path, "kavraiskiy_vii_wallpaper.jpg"))
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        return encoded_img_data

    def pass_json(self):
        i = 0
        for item in self.coordinates:
            self.json_obj["y_cords_" + str(i)] = item["Latitude"].to_list()
            self.json_obj["x_cords_" + str(i)] = item["Longitude"].to_list()
            i = i + 1

    def main(self, location_data=[["LAX", "NRT"], ["JFK", "LAX"]]):

        self.format_data(location_data)

        self.get_coords()

        self.pass_json()

        return self.json_obj
