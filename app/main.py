# Import os, a standard library that helps build file paths
import os

# Import FastAPI, the library that builds our web server
from fastapi import FastAPI

# Import the tool that serves static files such as CSS
from fastapi.staticfiles import StaticFiles

# Import the router that holds all our web addresses (routes)
from app.routes.api import router

# Find the folder where this file (main.py) lives. This is the "app" folder
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the web server object
app = FastAPI()

# Any address starting with /static/ is answered from the app/static folder (CSS, logo)
app.mount("/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static")

# Add all our routes (pages and actions) to the server
app.include_router(router)