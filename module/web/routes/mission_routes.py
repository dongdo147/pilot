from fastapi import APIRouter, HTTPException, Request,Query
from fastapi.responses import FileResponse
from module.web.model.allmodel import MissionPayload
from pathlib import Path
from datetime import datetime
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Define your mission folder
mission_folder = Path("missions")
mission_folder.mkdir(parents=True, exist_ok=True)

# POST: Save mission
@router.post("/mission")
async def receive_mission(payload: MissionPayload):
    try:
        waypoints = payload.waypoints
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"waypoint_{timestamp}.json"
        file_path = mission_folder / filename

        metadata = {
            "created_at": datetime.now().isoformat(),
            "count": len(waypoints),
            "waypoints": [waypoint.dict() for waypoint in waypoints]
        }

        with open(file_path, 'w') as file:
            json.dump(metadata, file, indent=4)

        logger.info(f"Saved {len(waypoints)} waypoints to {filename}")
        return {"message": f"Saved {len(waypoints)} waypoints to {filename}"}
    except Exception as e:
        logger.error(f"Error saving waypoints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# GET: Render mission manager page
@router.get("/mission-manager")
async def mission_manager(request: Request):
    from module.web.web_server import templates  # Import at runtime to avoid circular import
    files_info = []
    for file_path in mission_folder.glob("*.json"):
        try:
            with open(file_path, 'r') as file:
                content = json.load(file)
                created_at = content.get("created_at", "unknown")
                files_info.append({
                    "filename": file_path.name,
                    "created_at": created_at
                })
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in file {file_path.name}")
            files_info.append({
                "filename": file_path.name,
                "created_at": "invalid JSON"
            })
    return templates.TemplateResponse("mission-manager.html", {
        "request": request,
        "waypoints": files_info
    })

# GET: View a specific mission
@router.get("/mission-manager/{filename}")
async def view_mission(filename: str):
    file_path = mission_folder / filename
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

# DELETE: Delete a specific mission
@router.delete("/mission-manager/{filename}")
async def delete_mission(filename: str):
    file_path = mission_folder / filename
    if not file_path.is_file() or file_path.suffix != '.json':
        raise HTTPException(status_code=404, detail="File not found or not a JSON file")
    try:
        file_path.unlink()
        logger.info(f"Deleted waypoint file {filename}")
        return {"message": f"Deleted {filename}"}
    except Exception as e:
        logger.error(f"Error deleting waypoint file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# GET: Download a mission file
@router.get("/mission-manager/download/{filename}")
async def download_mission(filename: str):
    file_path = mission_folder / filename
    if not file_path.is_file() or file_path.suffix != '.json':
        raise HTTPException(status_code=404, detail="File not found or not a JSON file")
    try:
        logger.info(f"Downloaded waypoint file {filename}")
        return FileResponse(file_path, media_type='application/json', filename=filename)
    except Exception as e:
        logger.error(f"Error downloading waypoint file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/api/translations")
async def get_translations(
    lang: str = Query("en"),
    section: str = Query(None)  # section là tùy chọn
):
    path = Path(f"translations/{lang}.json")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Language file not found")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if section:
            section_data = data.get(section)
            if section_data is None:
                raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
            return section_data

        return data  # trả toàn bộ nếu không truyền section
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading translation: {str(e)}")
