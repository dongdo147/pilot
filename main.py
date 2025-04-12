import threading
from module.mavlink import pixhawk_reader, pixhawk_sending
from module.nmea.humminbird_reader import connect_humminbird, read_nmea
from module.web.web_server import handle_nmea_data, handle_pixhawk_data
import uvicorn


def start_web_server():
  
    uvicorn.run("module.web.web_server:app", host="0.0.0.0", port=8000, reload=False)

# --- Đọc Pixhawk ---
def pixhawk_loop():
    try:
        master = pixhawk_reader.connect_pixhawk()
        if master is None:
            print("⛔ Pixhawk chưa kết nối. Dừng luồng Pixhawk.")
            return
        while True:
            
            data = pixhawk_reader.read_data(master)
            if data:
                handle_pixhawk_data(data)
                print(data)
    except Exception as e:
        print(f"💥 Lỗi trong Pixhawk loop: {e}")

# --- Đọc Humminbird ---
def humminbird_loop():
    humminbird = connect_humminbird()
    if humminbird is None:
        print("⛔ Không đọc được dữ liệu từ Humminbird.")
        return

    try:
        while True:
            nmea_line = read_nmea(humminbird)
            if nmea_line:
                 handle_nmea_data(nmea_line)
    except KeyboardInterrupt:
        print("\n🛑 Ngắt luồng Humminbird.")


# --- Chạy song song ---
if __name__ == '__main__':
    thread1 = threading.Thread(target=pixhawk_loop)
    thread2 = threading.Thread(target=humminbird_loop)
    thread3 = threading.Thread(target=start_web_server, daemon=True)
    thread1.start()
    thread2.start()
    thread3.start()
    try:
        thread1.join()
        thread2.join()
        thread3.join()
    except KeyboardInterrupt:
        print("\n🛑 Ngắt toàn bộ chương trình.")
