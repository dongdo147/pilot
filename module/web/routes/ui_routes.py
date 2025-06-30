from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import Request
from module.web.web_server import templates

def create_ui_router(nmea_data, pixhawk_data, camera_frame):
    router = APIRouter()

    @router.get("/")
    async def home(request: Request):
        return templates.TemplateResponse("home/home.html", {"request": request})
    @router.get("/data")
    async def get_data():
        return JSONResponse(content={"nmea_data": nmea_data, "pixhawk_data": pixhawk_data})

    @router.get("/power")
    async def power(request: Request):
        return templates.TemplateResponse("power.html", {"request": request})

    @router.get("/yacht")
    async def yacht(request: Request):
        return templates.TemplateResponse("yacht.html", {
            "request": request,
            "nmea_data": nmea_data,
            "pixhawk_data": pixhawk_data
        })

    @router.get("/camera")
    async def get_camera_frame():
        if not camera_frame or "image" not in camera_frame:
            raise HTTPException(status_code=404, detail="No camera frame available")
        return JSONResponse(content={"image": camera_frame["image"]})

    return router
