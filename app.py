# The main FastAPI import and Request object
from fastapi import FastAPI, Request, Response, HTTPException
# Used for returning HTML responses (JSON is default)
from fastapi.responses import HTMLResponse
# Used for generating HTML from templatized files
from fastapi.templating import Jinja2Templates
# Used for making static resources available to server
from fastapi.staticfiles import StaticFiles
# Used for running the app directly through Python
import uvicorn
# Used for encoding and decoding JSON data
import json
# Database
import sqlite3


# Specify the "app" that will run the routing
app = FastAPI()
# Specify where the HTML files are located
templates = Jinja2Templates(directory="templates")
# Specify where the static files are located
app.mount("/static", StaticFiles(directory="static"), name="static")
# Setup the database
db = sqlite3.connect("test.db")
db.cursor().execute('''CREATE TABLE IF NOT EXISTS projects
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        xml TEXT)''')
db.commit()
db.close()


# Routes

@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    print(f"Fetching projects from database...")
    db = sqlite3.connect("test.db")
    projects = db.cursor().execute("SELECT * FROM projects").fetchall()
    db.close()
    print(f"Fetched {len(projects)} projects from database!")
    return templates.TemplateResponse("index.html", {"request": request, "projects": projects})


# REST API

@app.post("/projects", status_code=201)
def post_project(data: dict):
    try:
        name = data["name"]
        xml = data["xml"]
    except KeyError as e:
        return HTTPException(status_code=400, detail=f"Missing required field: {e}")
    project = (name, xml)
    print(f"Adding project {project[0]} to database...")
    db = sqlite3.connect("test.db")
    db.cursor().execute("INSERT INTO projects (name, xml) VALUES (?, ?)", project)
    db.commit()
    db.close()
    print(f"Added project {project[0]} to database!")

@app.get("/projects")
def get_projects():
    print(f"Fetching projects from database...")
    db = sqlite3.connect("test.db")
    projects = db.cursor().execute("SELECT * FROM projects").fetchall()
    db.close()
    print(f"Fetched {len(projects)} projects from database!")
    return {"name": projects[0][1], "xml": projects[0][2]}


# If running the server directly from Python as a module
if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=31337, reload=True)