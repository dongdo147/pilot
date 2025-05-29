from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, model_validator
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import json
import cv2
import base64
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from module.mavlink import pixhawk_sending
from module.mavlink import pixhawk_reader
from typing import Optional

# Configure logging
logging.basicConfig(
    filename="log/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("DATABASE_NAME")
secret_key = os.getenv("SECRET_KEY")  # For JWT
algorithm = "HS256"

if not all([mongo_uri, database_name, secret_key]):
    raise RuntimeError("Missing required environment variables: MONGO_URI, DATABASE_NAME, or SECRET_KEY")

# MongoDB client setup
client = None
db = None
collection = None
command_collection = None
users_collection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, collection, command_collection, users_collection
    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]
    collection = db["data"]
    command_collection = db["command"]
    users_collection = db["users"]
    yield
    client.close()

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Mount static files
static_dir = "module/web/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Ensure directories exist
for folder in ["module/web/waypoint", "log"]:
    os.makedirs(folder, exist_ok=True)

# Jinja2 templates
templates = Jinja2Templates(directory="module/web/templates")

# Global data stores
nmea_data = {}
pixhawk_data = {}
camera_frame = {}
waypoint_folder = Path("module/web/waypoint")

# JWT and password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Pydantic models
class Waypoint(BaseModel):
    seq: int
    frame: int
    command: int
    current: int
    autocontinue: int
    param1: float
    param2: float
    param3: float
    param4: float
    x: float
    y: float
    z: float

class ParamSetPayload(BaseModel):
    param_id: str
    param_value: int

class MissionPayload(BaseModel):
    waypoints: list[Waypoint]

class PWMRequest(BaseModel):
    channel: int
    pwm: int
    step: int = 10
    delay: int = 50

    @model_validator(mode="after")
    def validate_pwm(self):
        if not (1 <= self.channel <= 8):
            raise ValueError("Channel must be between 1 and 8")
        if not (1000 <= self.pwm <= 2000):
            raise ValueError("PWM must be between 1000 and 2000")
        return self

class CustomCommandRequest(BaseModel):
    command_id: int
    param1: int = 0
    param2: int = 0
    param3: int = 0
    param4: int = 0
    param5: int = 0
    param6: int = 0
    param7: int = 0

class User(BaseModel):
    username: str
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# JWT authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# User registration and login endpoints
@app.post("/register")
async def register(user: UserCreate):
    """
    Register a new user and store in MongoDB.
    """
    try:
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = pwd_context.hash(user.password)
        user_data = {"username": user.username, "hashed_password": hashed_password}
        await users_collection.insert_one(user_data)
        logger.info(f"Registered new user: {user.username}")
        return {"message": f"User {user.username} registered successfully"}
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token.
    """
    try:
        user = await users_collection.find_one({"username": form_data.username})
        if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        logger.info(f"User {form_data.username} logged in")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Waypoint endpoints
@app.post("/waypoint")
async def receive_waypoints(payload: MissionPayload, current_user: dict = Depends(get_current_user)):
    """
    Receive and save waypoints to a JSON file using MissionPayload.
    """
    try:
        waypoints = payload.waypoints
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"waypoint_{timestamp}.json"
        file_path = waypoint_folder / filename

        metadata = {
            "created_at": datetime.now().isoformat(),
            "count": len(waypoints),
            "waypoints": [waypoint.dict() for waypoint in waypoints],
            "created_by": current_user["username"]
        }

        with open(file_path, 'w') as file:
            json.dump(metadata, file, indent=4)

        logger.info(f"User {current_user['username']} saved {len(waypoints)} waypoints to {filename}")
        return {"message": f"Saved {len(waypoints)} waypoints to {filename}"}
    except Exception as e:
        logger.error(f"Error saving waypoints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/waypoint-manager")
async def waypoint_manager():
    """
    List all waypoint JSON files with metadata.
    """
    files_info = []
    for file_path in waypoint_folder.glob("*.json"):
        try:
            with open(file_path, 'r') as file:
                content = json.load(file)
                created_at = content.get("created_at", "unknown")
                created_by = content.get("created_by", "unknown")
            files_info.append({
                "filename": file_path.name,
                "created_at": created_at,
                "created_by": created_by
            })
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in file {file_path.name}")
            files_info.append({
                "filename": file_path.name,
                "created_at": "invalid JSON",
                "created_by": "unknown"
            })
    return {"waypoints": files_info}

@app.get("/waypoint-manager/{filename}")
async def view_waypoint(filename: str):
    """
    View details of a specific waypoint file.
    """
    file_path = waypoint_folder / filename
    if not file_path.is_file() or file_path.suffix != '.json':
        raise HTTPException(status_code=404, detail="File not found or not a JSON file")
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return {"data": data}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file {filename}")
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Error reading waypoint file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.delete("/waypoint-manager/{filename}")
async def delete_waypoint(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a specific waypoint file.
    """
    file_path = waypoint_folder / filename
    if not file_path.is_file() or file_path.suffix != '.json':
        raise HTTPException(status_code=404, detail="File not found or not a JSON file")
    try:
        file_path.unlink()
        logger.info(f"User {current_user['username']} deleted waypoint file {filename}")
        return {"message": f"Deleted {filename}"}
    except Exception as e:
        logger.error(f"Error deleting waypoint file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/waypoint-manager/download/{filename}")
async def download_waypoint(filename: str):
    """
    Download a specific waypoint file.
    """
    file_path = waypoint_folder / filename
    if not file_path.is_file() or file_path.suffix != '.json':
        raise HTTPException(status_code=404, detail="File not found or not a JSON file")
    try:
        logger.info(f"Downloaded waypoint file {filename}")
        return FileResponse(file_path, media_type='application/json', filename=filename)
    except Exception as e:
        logger.error(f"Error downloading waypoint file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# General endpoints
@app.get("/")
async def home(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/data")
async def get_data():
    """
    Return current NMEA and Pixhawk data.
    """
    return JSONResponse(content={"nmea_data": nmea_data, "pixhawk_data": pixhawk_data})

@app.get("/control")
async def control(request: Request):
    """
    Render the control page.
    """
    return templates.TemplateResponse("control.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Render the dashboard page with NMEA and Pixhawk data.
    """
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "nmea_data": nmea_data,
        "pixhawk_data": pixhawk_data
    })

@app.get("/camera")
async def get_camera_frame():
    """
    Return the latest camera frame as base64-encoded JPEG.
    """
    if not camera_frame or "image" not in camera_frame:
        raise HTTPException(status_code=404, detail="No camera frame available")
    return JSONResponse(content={"image": camera_frame["image"]})

# Data handling functions
async def handle_nmea_data(data: dict):
    """
    Update NMEA data and save to MongoDB.
    """
    if not data:
        return
    nmea_data.update(data)
    try:
        await collection.update_one(
            {"name": "firstboat"},
            {"$set": {"nmea_data": data}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating NMEA data in MongoDB: {str(e)}")

async def handle_pixhawk_data(data: dict):
    """
    Update Pixhawk data and save to MongoDB.
    """
    data_type = data.get("type")
    if not data_type:
        return
    pixhawk_data.update(data)
    data_subset = {k: v for k, v in data.items() if k != "type"}
    try:
        await collection.update_one(
            {"name": "firstboat"},
            {"$set": {f"pixhawk_data.{data_type}": data_subset}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating Pixhawk data in MongoDB: {str(e)}")

async def handle_camera_frame(frame):
    """
    Encode camera frame as JPEG and save to MongoDB.
    """
    if frame is None or frame.size == 0:
        logger.warning("Invalid or empty camera frame")
        return
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        logger.error("Failed to encode camera frame")
        return
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    camera_frame["image"] = jpg_as_text
    try:
        await collection.update_one(
            {"name": "firstboat"},
            {"$set": {"camera_frame": camera_frame}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating camera frame in MongoDB: {str(e)}")

async def handle_get_command():
    """
    Process commands from MongoDB and send to Pixhawk.
    """
    try:
        data = await command_collection.find_one({"name": "firstboat"})
        if not data or "command" not in data:
            logger.info("No command found")
            return None

        command = data["command"]
        if command.get("recive", True):
            return None

        command_type = command.get("type")
        success = False

        if command_type == "custom_command":
            success = pixhawk_sending.send_custom_command(
                command.get("command_id", 0),
                command.get("param1", 0),
                command.get("param2", 0),
                command.get("param3", 0),
                command.get("param4", 0),
                command.get("param5", 0),
                command.get("param6", 0),
                command.get("param7", 0)
            )
        elif command_type == "send_arm_command":
            success = pixhawk_sending.send_arm_command()
        elif command_type == "send_pwm":
            success = pixhawk_sending.send_pwm(
                command.get("channel", 0),
                command.get("pwm", 0),
                step=command.get("step", 10),
                delay=command.get("delay", 50)
            )

        if success:
            await command_collection.update_one(
                {"name": "firstboat"},
                {"$set": {"command.recive": True}}
            )
        return success
    except Exception as e:
        logger.error(f"Error handling command: {str(e)}")
        return None

# Pixhawk control endpoints
@app.get("/health")
async def health():
    """
    Check the health status of the API.
    """
    return {"status": "ok"}

@app.post("/api/send_pwm")
async def api_send_pwm(req: PWMRequest, current_user: dict = Depends(get_current_user)):
    """
    Send a PWM signal to a specified Pixhawk channel.
    """
    try:
        success = pixhawk_sending.send_pwm(req.channel, req.pwm, step=req.step, delay=req.delay)
        logger.info(f"User {current_user['username']} sent PWM to channel {req.channel}")
        return {
            "status": "ok" if success else "error",
            "channel": req.channel,
            "pwm": req.pwm,
            "step": req.step,
            "delay": req.delay
        }
    except Exception as e:
        logger.error(f"Error sending PWM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send PWM: {str(e)}")

@app.post("/api/send_arm_command")
async def api_send_arm_command(current_user: dict = Depends(get_current_user)):
    """
    Send an arm command to the Pixhawk.
    """
    try:
        success = pixhawk_sending.send_arm_command()
        logger.info(f"User {current_user['username']} sent arm command")
        return {"status": "ok" if success else "error"}
    except Exception as e:
        logger.error(f"Error sending arm command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send arm command: {str(e)}")

@app.post("/api/send_custom_command")
async def api_send_custom_command(command: CustomCommandRequest, current_user: dict = Depends(get_current_user)):
    """
    Send a custom command to the Pixhawk.
    """
    try:
        success = pixhawk_sending.send_custom_command(
            command.command_id, command.param1, command.param2, command.param3,
            command.param4, command.param5, command.param6, command.param7
        )
        logger.info(f"User {current_user['username']} sent custom command {command.command_id}")
        return {"status": "ok" if success else "error"}
    except Exception as e:
        logger.error(f"Error sending custom command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send custom command: {str(e)}")

@app.post("/api/set_param")
async def set_param(payload: ParamSetPayload, current_user: dict = Depends(get_current_user)):
    """
    Set a parameter on the Pixhawk.
    """
    try:
        if not payload.param_id or not isinstance(payload.param_value, int):
            raise HTTPException(status_code=400, detail="Invalid param_id or param_value")
        success, message = pixhawk_sending.set_param_value(payload.param_id, payload.param_value)
        if success:
            logger.info(f"User {current_user['username']} set parameter {payload.param_id}")
            return {"status": "ok", "message": "Parameter set successfully"}
        raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        logger.error(f"Error setting parameter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set parameter: {str(e)}")

@app.get("/api/get_mission")
async def get_mission(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the current mission from the Pixhawk.
    """
    try:
        success, result = pixhawk_reader.readMission()
        if not success:
            raise HTTPException(status_code=500, detail=result)
        logger.info(f"User {current_user['username']} retrieved mission")
        return {"status": "success", "missions": result}
    except Exception as e:
        logger.error(f"Error getting mission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get mission: {str(e)}")

@app.post("/api/send_mission")
async def send_mission(payload: MissionPayload, current_user: dict = Depends(get_current_user)):
    """
    Send a mission (waypoints) to the Pixhawk.
    """
    try:
        success, result = pixhawk_sending.send_mission(payload.waypoints)
        if not success:
            raise HTTPException(status_code=500, detail=result)
        logger.info(f"User {current_user['username']} sent mission with {len(payload.waypoints)} waypoints")
        return {"status": "success", "missions": result}
    except Exception as e:
        logger.error(f"Error sending mission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send mission: {str(e)}")
