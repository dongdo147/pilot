from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import cv2
import base64
import logging
from pathlib import Path
from module.mavlink import pixhawk_sending
from module.web.configs.mongodb import lifespan,get_db 

# Configure logging
logging.basicConfig(
    filename="log/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)
# Mount static files
static_dir = "module/web/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Ensure directories exist
for folder in ["module/web/mission", "log"]:
    os.makedirs(folder, exist_ok=True)
# Jinja2 templates
templates = Jinja2Templates(directory="module/web/templates")


# Global data stores
nmea_data = {}
pixhawk_data = {}
camera_frame = {}
mission_folder = Path("module/web/mission")  # Updated from waypoint_folder
templates.env.globals["url_for"] = lambda name, **path_params: f"/static/{path_params.get('filename', '')}"



async def handle_nmea_data(data: dict):
    """
    Update NMEA data and save to MongoDB.
    """
    if not data:
        return
    nmea_data.update(data)

    try:
        db = get_db()
        await db["data"].update_one(
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
        db = get_db()
        await db["data"].update_one(
            {"name": "firstboat"},
            {"$set": {f"pixhawk_data.{data_type}": data_subset}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating Pixhawk data in MongoDB: {str(e)}")

async def handle_camera_frame(frame):

    if frame is None or frame.size == 0:
        print("⚠️ Frame is None or empty")
        return

    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("⚠️ Lỗi khi encode ảnh từ frame")
        return

    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    camera_frame.clear()
    camera_frame.update({"image": jpg_as_text})

    try:
        db = get_db()
        await db["data"].update_one(
            {"name": "firstboat"},
            {"$set": {"camera_frame": camera_frame}},
            upsert=True
        )
    except Exception as e:
        print(f"💥 Lỗi update MongoDB: {str(e)}")

async def handle_get_command():
    """
    Process commands from MongoDB and send to Pixhawk.
    """
    try:
        db = get_db()
        command_doc = await db["command"].find_one({"name": "firstboat"})
        if not command_doc or "command" not in command_doc:
            logger.info("No command found")
            return None

        command = command_doc["command"]
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
            await db["command"].update_one(
                {"name": "firstboat"},
                {"$set": {"command.recive": True}}
            )
        return success
    except Exception as e:
        logger.error(f"Error handling command: {str(e)}")
        return None

# Mission endpoints (updated from waypoint)
from module.web.routes.mission_routes import router as mission_router
app.include_router(mission_router)
# General endpoints (unchanged)
from module.web.routes.ui_routes import create_ui_router
app.include_router(create_ui_router(nmea_data, pixhawk_data, camera_frame))
# Pixhawk control endpoints (unchanged)
from module.web.routes.pixhawk_routes import router as pixhawk_router
app.include_router(pixhawk_router)
# Data handling functions (unchanged)
from module.web.routes.mission_routes import router as translation_router
app.include_router(translation_router)

