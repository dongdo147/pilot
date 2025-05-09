-- Cấu hình
local input_ch1       = 1       -- Throttle left
local input_ch2       = 2       -- Throttle right
local servo_left_ch   = 4       -- Servo azimuth trái
local servo_right_ch  = 5       -- Servo azimuth phải

local pwm_straight    = 1500    -- PWM khi đi thẳng (90 độ)
local pwm_left_max    = 2200    -- PWM khi quay trái hết (180 độ)
local pwm_right_min   = 800     -- PWM khi quay phải hết (0 độ)
local diff_max        = 350     -- Độ lệch lớn nhất để tính
local interval        = 200     -- ms (chu kỳ cập nhật)

-- Hàm giới hạn giá trị PWM trong khoảng an toàn
local function clamp_pwm(pwm)
    return math.max(800, math.min(2200, pwm))
end

-- Hàm ánh xạ chênh lệch sang PWM servo
local function map_diff_to_servo_pwm(diff)
    if math.abs(diff) < 5 then
        return pwm_straight
    elseif diff > 0 then
        -- Rẽ trái: PWM tăng từ 1500 → 2200
        local ratio = math.min(diff / diff_max, 1.0)
        return clamp_pwm(math.floor(pwm_straight + ratio * (pwm_left_max - pwm_straight)))
    else
        -- Rẽ phải: PWM giảm từ 1500 → 800
        local ratio = math.min(-diff / diff_max, 1.0)
        return clamp_pwm(math.floor(pwm_straight - ratio * (pwm_straight - pwm_right_min)))
    end
end

-- Kiểm tra các module cần thiết
if not rc or not SRV_Channels or not gcs then
    return
end

-- Hàm chính
local function update()
    local pwm1 = rc:get_pwm(input_ch1)
    local pwm2 = rc:get_pwm(input_ch2)

    if pwm1 and pwm2 then
        local diff = pwm1 - pwm2  -- Đảo chiều servo tại đây nếu cần

        local pwm_servo = map_diff_to_servo_pwm(diff)

        -- Gửi PWM tới 2 kênh servo azimuth
        SRV_Channels:set_output_pwm_chan(servo_left_ch  - 1, pwm_servo)
        SRV_Channels:set_output_pwm_chan(servo_right_ch - 1, pwm_servo)

        -- Debug log
        gcs:send_text(6, string.format(
            "CH1=%d CH2=%d → Diff=%d → Servo PWM=%d",
            pwm1, pwm2, diff, pwm_servo
        ))
    else
        gcs:send_text(6, "Không đọc được CH1 hoặc CH2")
    end

    return update, interval
end

gcs:send_text(6, "Azimuth servo control script started")
return update()
