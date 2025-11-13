from fastapi import FastAPI, Request, HTTPException, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
import time
from pydantic import BaseModel
from pymongo import MongoClient
import middleware
from middleware import AdvancedMiddleware
from database import db
from fastapi.templating import Jinja2Templates
import auth


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(AdvancedMiddleware)
# `auth.router` already defines its own prefix; include it without adding another prefix to avoid paths like /auth/auth
app.include_router(auth.router)

# Serve the index page at root BEFORE including other routers that may define '/'
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

app.include_router(middleware.router)

# Serve static files (css/js/images) from the ./static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# HTML login form (renders templates/login.html)
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
	return templates.TemplateResponse("login.html", {"request": request})


# Handle form submission (posts form data and renders result template)
@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
	# use the existing auth.authenticate_user helper
	user = await auth.authenticate_user(username, password, db)
	if not user:
		# render the same form with an error message
		return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

	token = auth.create_access_token(user["username"], str(user["_id"]), timedelta(minutes=20))
	return templates.TemplateResponse("login_result.html", {"request": request, "username": user["username"], "token": token})


# HTML signup form (renders templates/signup.html)
@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
	return templates.TemplateResponse("signup.html", {"request": request})


# Handle signup submission (posts form data and creates a new user)
@app.post("/signup", response_class=HTMLResponse)
async def signup_submit(request: Request, username: str = Form(...), password: str = Form(...)):
	# Check if user already exists
	existing_user = await db["users"].find_one({"username": username})
	if existing_user:
		return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
	
	# Hash password and create user
	hashed_pw = auth.bcrypt_context.hash(password)
	result = await db["users"].insert_one({
		"username": username,
		"hashed_password": hashed_pw
	})
	
	return templates.TemplateResponse("signup_result.html", {"request": request, "username": username, "user_id": str(result.inserted_id)})