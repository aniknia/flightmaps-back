from flightmapper_back import app
from flightmapper_module import flightmapper

flight_app = flightmapper.Action()

# TODO: add version control


@app.get("/v1/")
def default():
    return {"default": True}


@app.get("/v1/{route_start}/{route_end}")
def get_routes(route_start: str, route_end: str):
    route = flight_app.main([[route_start, route_end]])
    return {"x_cords": route["x_cords_0"], "y_cords": route["y_cords_0"]}


@app.get("/v1/check_code/{check_code}")
def check_code(check_code: str):
    if flight_app.airport_search(check_code) != False:
        return {"check_code": True}
    else:
        return {"check_code": False}
