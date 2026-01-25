#pages.py has the routes for the websites I want my users to be able to visit
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)                    #creates blueprint that groups related routes together

@pages_bp.route("/") #home page
def home():
    return render_template("home.html", active_page="home")     #must use render_template to render the html files from the templates folder in module 1

@pages_bp.route("/contact") #contact page
def contact():
    return render_template("contact.html", active_page="contact")  #active page variable is used so that the selected tab is highlighted

@pages_bp.route("/projects") #projects page
def projects():
    return render_template("projects.html", active_page="projects")

#using Blueprints helps keep the code organized and scalable