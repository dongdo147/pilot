from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import  JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
import cv2
from module.mavlink import pixhawk_sending
from datetime import datetime
from pydantic import BaseModel
import base64

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("DATABASE_NAME")
class ParamPayload(BaseModel):
    param_id: str
    param_value: int


client = MongoClient(mongo_uri)
db = client[database_name]
collection = db["data"]


app = FastAPI()
nmea_data = {}
pixhawk_data = {}
camera_frame = {}
waypoints_data={}
waypoint_folder = "module/web/waypoint"
for folder in ["module/web/waypoint", "log"]:
    os.makedirs(folder, exist_ok=True)
templates = Jinja2Templates(directory="module/web/templates")
class PWMRequest(BaseModel):
    channel: int
    pwm: int
    step: int = 10    # Mặc định là bước 10
    delay: int = 50   # Mặc định là delay 50ms
class CustomCommandRequest(BaseModel):
    command_id: int
    param1: int = 0
    param2: int = 0
    param3: int = 0
    param4: int = 0
    param5: int = 0
    param6: int = 0
    param7: int = 0


# -----------MẤY CÁI NÀY LÀ LIÊN QUAN TỚI LƯU  VÀ QUẢN LÝ WAYPOINTS-----------

#1 Nhận waypoint từ client
app.mount("/static", StaticFiles(directory="module/web/static"), name="static")
@app.post("/waypoint")
async def receive_waypoints(request: Request):
    data = await request.json()
    waypoints = data.get("waypoints", [])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"waypoint_{timestamp}.json"
    file_path = os.path.join(waypoint_folder, filename)

    metadata = {
        "created_at": datetime.now().isoformat(),
        "count": len(waypoints),
        "waypoints": waypoints,
    }

    with open(file_path, 'w') as file:
        json.dump(metadata, file, indent=4)

    with open("log/waypoint_log.txt", 'a') as log_file:
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đã lưu {len(waypoints)} waypoint vào {filename}\n")

    return {"message": f"Đã lưu {len(waypoints)} waypoint vào {filename}"}
#2 Xem danh sách các file json chứa waypoint
@app.get("/waypoint-manager")
async def waypoint_manager():
    files_info = []
    for f in os.listdir(waypoint_folder):
        if f.endswith('.json'):
            path = os.path.join(waypoint_folder, f)
            try:
                with open(path, 'r') as file:
                    content = json.load(file)
                    created_at = content.get("created_at", "unknown")
            except:
                created_at = "unknown"
            files_info.append({"filename": f, "created_at": created_at})
    return {"waypoints": files_info}

#3 Hình như là xem chi tiết 1 file cụ thể á
@app.get("/waypoint-manager/{filename}")
async def view_waypoint(filename: str):
    file_path = os.path.join(waypoint_folder, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
       
        return {"data": data}
    else:
        return {"error": "File không tồn tại"}
#4 Thấy ko cần thì xóa file thoai
@app.delete("/waypoint-manager/{filename}")
async def delete_waypoint(filename: str):
    file_path = os.path.join(waypoint_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        with open("log/waypoint_log.txt", 'a') as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đã xóa file {filename}\n")
        return {"message": f"Đã xóa {filename}"}
    else:
        return {"error": "File không tồn tại"}
#4 Cái này để tải về coi nè, làm gì thì tui hok bíc
@app.get("/waypoint-manager/download/{filename}")
async def download_waypoint(filename: str):
    file_path = os.path.join(waypoint_folder, filename)
    if os.path.exists(file_path):
        with open("log/waypoint_log.txt", 'a') as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đã tải file {filename}\n")
        return FileResponse(file_path, media_type='application/json', filename=filename)
    else:
        return {"error": "File không tồn tại"}

# -------MẤY CÁI NÀY CHƯA GHI CHÚ ĐỢI SUY NGHĨ ĐÃ----------
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
@app.get("/data")
def get_data():
    return JSONResponse(content={"nmea_data":nmea_data,"pixhawk_data":pixhawk_data})
@app.get("/control")
async def control(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request,"nmea_data":nmea_data,"pixhawk_data":pixhawk_data})

@app.get("/camera")
def get_camera_frame():
    if "image" in camera_frame:
        return JSONResponse(content={"image": camera_frame["image"]})
    else:
        return JSONResponse(content={"error": "No camera frame available"}, status_code=404)
def handle_nmea_data(data: dict):
    nmea_data.update(data)
    if not data:
        return
    collection.update_one({"name": "firstboat"}, {"$set": {"nmea_data":data}}, upsert=True)
def handle_pixhawk_data(data: dict):
    data2={}
    pixhawk_data.update(data)
    data_type = data.get("type")
    if not data_type:
        return
    data2[data_type] = {k: v for k, v in data.items() if k != "type"}
    # Cập nhật riêng phần đó lên MongoDB

    collection.update_one(
        {"name": "firstboat"},
        {f"$set": {f"pixhawk_data.{data_type}": data2[data_type]}},
        upsert=True
    )

def handle_camera_frame(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    camera_frame["image"] = jpg_as_text
    if not camera_frame:
        return
    collection.update_one({"name": "firstboat"}, {"$set": {"camera_frame":camera_frame}}, upsert=True)
def handle_get_command():
    data =  db["command"].find_one({"name": "firstboat"})
    command = data.get("command") if data else None
   
    if not command:
        print("Ko có lệnh")
        return None
    
    # Giả sử command là dict
    if command.get("type") == "custom_command" and command.get("recive") == False:
        print(command)
        success =  pixhawk_sending.send_custom_command(
            command.get("command_id", 0),
            command.get("param1", 0),
            command.get("param2", 0),
            command.get("param3", 0),
            command.get("param4", 0),
            command.get("param5", 0),
            command.get("param6", 0),
            command.get("param7", 0)
        )
        db["command"].update_one(
            {"name": "firstboat"},
            {"$set": {"command.recive": True}}
        )
        return success
    elif command.get("type") == "send_arm_command" and command.get("recive") == False:
        success =  pixhawk_sending.send_arm_command()
        db["command"].update_one(
            {"name": "firstboat"},
            {"$set": {"command.recive": True}}
        )
        return success
    elif command.get("type")== "send_pwm" and command.get("recive")==False:
        db["command"].update_one(
            {"name": "firstboat"},
            {"$set": {"command.recive": True}}
        )
        success =  pixhawk_sending.send_pwm(
            command.get("channel"), 
            command.get("pwm"), 
            step=command.get("step"), 
            delay=command.get("delay")
            )
        return success
  
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/api/send_pwm")
def api_send_pwm(req: PWMRequest):
    # Gọi hàm send_pwm với tất cả các tham số
    success =  pixhawk_sending.send_pwm(req.channel, req.pwm, step=req.step, delay=req.delay)
    
    return {
        "status": "ok" if success else "error",
        "channel": req.channel,
        "pwm": req.pwm,
        "step": req.step,
        "delay": req.delay
    }

@app.post("/api/send_arm_command")
def api_send_arm_command():
    success =  pixhawk_sending.send_arm_command()
    return {
        "status": "ok" if success else "error"
    }
@app.post("/api/send_custom_command")
def api_send_custom_command(command: CustomCommandRequest):
    success =  pixhawk_sending.send_custom_command(
        command.command_id, command.param1, command.param2, command.param3, 
        command.param4, command.param5, command.param6, command.param7
    )
    return {
        "status": "ok" if success else "error"
    }
@app.post("/api/set_param")
def set_param(payload: ParamPayload):
    param_id = payload.param_id
    param_value = payload.param_value
    
    # Kiểm tra param_id và param_value
    if not param_id or not isinstance(param_value, int):
        raise HTTPException(status_code=400, detail="param_id hoặc param_value không hợp lệ")
    
    # Gọi hàm set_param_value
    success, message = pixhawk_sending.set_param_value(param_id, param_value)
    if success:
        return {"status": "ok", "message": "set param thành công"}
    raise HTTPException(status_code=500, detail=message)




    
