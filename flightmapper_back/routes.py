from flightmapper_back import app
from flightmapper_module import flightmapper

flight_app = flightmapper.Action()

# TODO: add version control


@app.get("/v1/")
def default():
    return {"default": True}


# TODO: add error handling


@app.get("/v1/check-code/{check_code}")
def check_code(check_code: str):
    if flight_app.airport_search(check_code) != False:
        return {"check_code": True}
    else:
        return {"check_code": False}


@app.get("/v1/get-route/{route_start}/{route_end}")
def get_route(route_start: str, route_end: str):
    route = flight_app.main([[route_start, route_end]])
    return {
        "error": False,
        "x_cords": route["x_cords_0"],
        "y_cords": route["y_cords_0"],
    }


@app.get("/v1/get-time/{route_start}/{route_end}")
def get_time(route_start: str, route_end: str):
    return {
        "error": False,
        "time": 0,
    }


@app.get("/v1/get-distance/{route_start}/{route_end}")
def get_distance(route_start: str, route_end: str):
    return {
        "error": False,
        "distance": 0,
    }


@app.get("/v1/get-carbon/{route_start}/{route_end}")
def get_carbon(route_start: str, route_end: str):
    return {
        "error": False,
        "carbon": 0,
    }
