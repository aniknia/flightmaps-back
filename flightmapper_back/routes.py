from flightmapper_back import app
from flightmapper_module import flightmapper_function

# TODO: add version control


@app.get("/")
def default():
    return {"default": True}


# TODO: add error handling


@app.get("/check-code/{check_code}")
def check_code(check_code: str):
    if flightmapper_function.airport_search(check_code) != False:
        return {"check_code": True}
    else:
        return {"check_code": False}


@app.get("/get-route/{route_start}/{route_end}")
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
