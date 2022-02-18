from flightmapper_back import app

# TODO: add version control
@app.get("/v1/{route_start}/{route_end}")
def get_routes(route_start: str, route_end: str):
    return {"x_cords": [], "y_cords": []}
