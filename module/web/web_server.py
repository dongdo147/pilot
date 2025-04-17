from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
import cv2
from module.mavlink import pixhawk_sending
from datetime import datetime
from pydantic import BaseModel
import base64
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
def handle_nmea_data(data: dict):
    nmea_data.update(data)
@app.get("/camera")
def get_camera_frame():
    if "image" in camera_frame:
  
        return JSONResponse(content={"image": camera_frame["image"]})
    else:
        return JSONResponse(content={"error": "No camera frame available"}, status_code=404)

def handle_pixhawk_data(data: dict):
    pixhawk_data.update(data)
def handle_camera_frame(frame):
    # Chuyển frame (numpy.ndarray) thành ảnh JPEG encode
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    camera_frame["image"] = jpg_as_text
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/api/send_pwm")
async def api_send_pwm(req: PWMRequest):
    # Gọi hàm send_pwm với tất cả các tham số
    success = await pixhawk_sending.send_pwm(req.channel, req.pwm, step=req.step, delay=req.delay)
    
    return {
        "status": "ok" if success else "error",
        "channel": req.channel,
        "pwm": req.pwm,
        "step": req.step,
        "delay": req.delay
    }

