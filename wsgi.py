from wsgiref.simple_server import make_server
from app import app


with make_server("", 5000, app) as server:
    print(
        "serving on port 5000...\nvisit http://127.0.0.1:5000\nTo exit press ctrl + c"
    )
    server.serve_forever()
