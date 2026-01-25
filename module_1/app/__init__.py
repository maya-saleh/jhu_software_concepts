#registers the blueprints for Flask so it can easily follow routes
from flask import Flask

def create_app():
    app = Flask(__name__)

    from .pages import pages_bp
    app.register_blueprint(pages_bp)

    return app

#this helps as the project grows and the app setup is in one place