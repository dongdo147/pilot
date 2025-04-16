-- Script: sweep_servo.lua
-- Quét servo kênh 9 từ 800 đến 2200 và ngược lại

local channel = 9     -- Số kênh servo (kênh 9)
local min_pwm = 800
local max_pwm = 2200
local step = 20
local delay = 100    -- milliseconds

local pwm = min_pwm
local going_up = true
local last_time = 0

function update()
    local now = millis()

    if now - last_time >= delay then
        -- Gửi PWM đến kênh servo (channel - 1 vì ArduPilot dùng 0-based index)
        SRV_Channels:set_output_pwm_chan_timeout(channel - 1, pwm, delay)

        -- Cập nhật giá trị tiếp theo
        if going_up then
            pwm = pwm + step
            if pwm >= max_pwm then
                pwm = max_pwm
                going_up = false
            end
        else
            pwm = pwm - step
            if pwm <= min_pwm then
                pwm = min_pwm
                going_up = true
            end
        end

        last_time = now
    end

    return update, 100  -- Gọi lại sau 100ms
end

return update()
