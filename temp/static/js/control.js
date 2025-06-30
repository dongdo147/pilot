 const pwmSlider = document.getElementById("pwm");
    const pwmValueDisplay = document.getElementById("pwm-value");
    const resultMsg = document.getElementById("result-msg");

    pwmSlider.addEventListener("input", () => {
        pwmValueDisplay.textContent = pwmSlider.value;
    });

    function showResult(success, message) {
        resultMsg.textContent = message;
        resultMsg.classList.toggle("text-green-600", success);
        resultMsg.classList.toggle("text-red-600", !success);
    }

    async function postCommand(url, payload) {
        try {
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            return await res.json();
        } catch {
            return { status: "error" };
        }
    }

    document.getElementById("submit-btn").addEventListener("click", async () => {
        const command = document.getElementById("command").value;
        let payload;
        let url;

        switch (command) {
            case "send_pwm":
                payload = {
                    channel: +document.getElementById("channel").value,
                    pwm: +pwmSlider.value,
                    step: +document.getElementById("step").value,
                    delay: +document.getElementById("delay").value,
                };
                url = "/api/send_pwm";  // URL riêng cho lệnh PWM
                break;
            case "armed":
                payload = { command_id: 400, param1: 1 };
                url = "/api/send_custom_command"; // URL chung cho các lệnh khác
                break;
            case "disarmed":
                payload = { command_id: 400, param1: 0 };
                url = "/api/send_custom_command"; // URL chung cho các lệnh khác
                break;
            case "reboot":
                payload = { command_id: 246, param1: 1 };
                url = "/api/send_custom_command"; // URL chung cho các lệnh khác
                break;
            case "set_param_safety":
                payload = {
                    param_id: "BRD_SAFETYENABLE",
                    param_value: 0
                    };
                url = "/api/set_param"; // API riêng
                break;
            default:
                break;
        }

        const result = await postCommand(url, payload);
        if (result.status === "ok") {
            showResult(true, `✅ Lệnh ${command} đã được gửi thành công.`);
        } else {
            showResult(false, "❌ Gửi lệnh thất bại. Kiểm tra kết nối Pixhawk.");
        }
    });