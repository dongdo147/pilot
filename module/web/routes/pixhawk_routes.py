
# module/routes/pixhawk_routes.py
from fastapi import APIRouter, HTTPException
from module.web.model.allmodel import PWMRequest, CustomCommandRequest, ParamSetPayload, MissionPayload
from module.mavlink import pixhawk_sending, pixhawk_reader
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/api/send_pwm")
async def api_send_pwm(req: PWMRequest):
    try:
        success = pixhawk_sending.send_pwm(req.channel, req.pwm, step=req.step, delay=req.delay)
        logger.info(f"Sent PWM to channel {req.channel}")
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

@router.post("/api/send_arm_command")
async def api_send_arm_command():
    try:
        success = pixhawk_sending.send_arm_command()
        logger.info("Sent arm command")
        return {"status": "ok" if success else "error"}
    except Exception as e:
        logger.error(f"Error sending arm command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send arm command: {str(e)}")

@router.post("/api/send_custom_command")
async def api_send_custom_command(command: CustomCommandRequest):
    try:
        success = pixhawk_sending.send_custom_command(
            command.command_id, command.param1, command.param2, command.param3,
            command.param4, command.param5, command.param6, command.param7
        )
        logger.info(f"Sent custom command {command.command_id}")
        return {"status": "ok" if success else "error"}
    except Exception as e:
        logger.error(f"Error sending custom command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send custom command: {str(e)}")

@router.post("/api/set_param")
async def set_param(payload: ParamSetPayload):
    try:
        if not payload.param_id or not isinstance(payload.param_value, int):
            raise HTTPException(status_code=400, detail="Invalid param_id or param_value")
        success, message = pixhawk_sending.set_param_value(payload.param_id, payload.param_value)
        if success:
            logger.info(f"Set parameter {payload.param_id}")
            return {"status": "ok", "message": "Parameter set successfully"}
        raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        logger.error(f"Error setting parameter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set parameter: {str(e)}")

@router.get("/api/get_mission")
async def get_mission():
    try:
        success, result = pixhawk_reader.readMission()
        if not success:
            raise HTTPException(status_code=500, detail=result)
        logger.info("Retrieved mission")
        return {"status": "success", "missions": result}
    except Exception as e:
        logger.error(f"Error getting mission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get mission: {str(e)}")

@router.post("/api/send_mission")
async def send_mission(payload: MissionPayload):
    try:
        success, result = pixhawk_sending.send_mission(payload.waypoints)
        if not success:
            raise HTTPException(status_code=500, detail=result)
        logger.info(f"Sent mission with {len(payload.waypoints)} waypoints")
        return {"status": "success", "missions": result}
    except Exception as e:
        logger.error(f"Error sending mission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send mission: {str(e)}")
