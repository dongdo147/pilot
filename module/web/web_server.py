from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
app = FastAPI()
nmea_data = {}
pixhawk_data = {}
templates = Jinja2Templates(directory="module/web/templates")
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
 
def handle_pixhawk_data(data: dict):
    pixhawk_data.update(data)
  
@app.get("/health")
def health():
    return {"status": "ok"}

