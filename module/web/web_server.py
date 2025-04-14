from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
import cv2
from datetime import datetime
import base64
app = FastAPI()
nmea_data = {}
pixhawk_data = {}
camera_frame = {}
waypoints_data={}
waypoint_folder = "module/web/waypoint"
if not os.path.exists(waypoint_folder):
    os.makedirs(waypoint_folder)
templates = Jinja2Templates(directory="module/web/templates")

# -----------MẤY CÁI NÀY LÀ LIÊN QUAN TỚI LƯU  VÀ QUẢN LÝ WAYPOINTS-----------

#1 Nhận waypoint từ client
app.mount("/static", StaticFiles(directory="module/web/static"), name="static")
@app.post("/waypoint")
async def save_waypoint(waypoints: list):
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

    with open("module/web/waypoint_log.txt", 'a') as log_file:
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đã lưu {len(waypoints)} waypoint vào {filename}\n")

    return {"message": f"Đã lưu {len(waypoints)} waypoint vào {filename}"}
#2 Xem danh sách các file json chứa waypoint
@app.get("/waypoint-manager")
async def waypoint_manager():
    files = [f for f in os.listdir(waypoint_folder) if f.endswith('.json')]
    return {"waypoints": files}
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
        return {"message": f"Đã xóa {filename}"}
    else:
        return {"error": "File không tồn tại"}
#4 Cái này để tải về coi nè, làm gì thì tui hok bíc
@app.get("/waypoint-manager/download/{filename}")
async def download_waypoint(filename: str):
    file_path = os.path.join(waypoint_folder, filename)
    if os.path.exists(file_path):
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

