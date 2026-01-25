from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def home():
    return render_template("home.html", active_page="home")

@pages_bp.route("/contact")
def contact():
    return render_template("contact.html", active_page="contact")

@pages_bp.route("/projects")
def projects():
    return render_template("projects.html", active_page="projects")