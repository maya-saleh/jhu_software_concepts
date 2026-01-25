# imports flask app and makes sure the server runs on the corect host and port
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
