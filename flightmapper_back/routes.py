from flightmapper_back import app
from flightmapper_module import flightmapper_function

# TODO: add version control


@app.get("/v1/")
def default():
    return {"default": True}


# TODO: add error handling


@app.get("/v1/check-code/{check_code}")
def check_code(check_code: str):
    if flightmapper_function.airport_search(check_code) != False:
        return {"check_code": True}
    else:
        return {"check_code": False}


@app.get("/v1/get-route/{route_start}/{route_end}")
def get_route(route_start: str, route_end: str):
    route = flightmapper_function.main([route_start, route_end])
    if route:
        return {
            "error": False,
            "x": route["x"],
            "y": route["y"],
            "time": route["time"],
            "distance": route["distance"],
            "carbon": route["carbon"],
        }
    else:
        return {"error": True}


@app.get("/v1/get-time/{route_start}/{route_end}")
def get_time(route_start: str, route_end: str):
    time = flightmapper_function.main([route_start, route_end])
    if time:
        return {
            "error": False,
            "time": time["time"],
        }
    else:
        return {"error": True}


@app.get("/v1/get-distance/{route_start}/{route_end}")
def get_distance(route_start: str, route_end: str):
    distance = flightmapper_function.main([route_start, route_end])
    if distance:
        return {
            "error": False,
            "distance": distance["distance"],
        }
    else:
        return {"error": True}


@app.get("/v1/get-carbon/{route_start}/{route_end}")
def get_carbon(route_start: str, route_end: str):
    carbon = flightmapper_function.main([route_start, route_end])
    if carbon:
        return {
            "error": False,
            "carbon": carbon["carbon"],
        }
    else:
        return {"error": True}
