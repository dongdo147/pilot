from pydantic import BaseModel, model_validator

# Waypoint model
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
# MissionPayload model
class MissionPayload(BaseModel):
    waypoints: list[Waypoint]

# ParamSetPayload model
class ParamSetPayload(BaseModel):
    param_id: str
    param_value: int


# PWMRequest model
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

# CustomCommandRequest model
class CustomCommandRequest(BaseModel):
    command_id: int
    param1: int = 0
    param2: int = 0
    param3: int = 0
    param4: int = 0
    param5: int = 0
    param6: int = 0
    param7: int = 0
