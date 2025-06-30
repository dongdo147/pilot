import asyncio
from module.mavlink import pixhawk_reader, pixhawk_sending
from module.camera.usb_camera_module import USBCamera
from module.nmea.humminbird_reader import connect_humminbird, read_nmea
from module.web.web_server import handle_nmea_data, handle_pixhawk_data, handle_camera_frame, handle_get_command
import uvicorn

async def start_web_server():
    config = uvicorn.Config("module.web.web_server:app", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()

async def database_loop():
    try:
        while True:
            await handle_get_command()
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"Lỗi trong database_loop: {e}")

async def pixhawk_loop():
    master = None
    while master is None:
        try:
            master = await asyncio.to_thread(pixhawk_reader.connect_pixhawk)
            if master is None:
                print("⛔ Pixhawk chưa kết nối. Thử lại sau 3 giây...")
                await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️ Lỗi khi cố gắng kết nối Pixhawk: {e}")
            await asyncio.sleep(3)

    print("✅ Pixhawk đã kết nối.")
    pixhawk_sending.set_master(master)

    try:
        while True:
            data = await asyncio.to_thread(pixhawk_reader.read_data, master)
            if data:
                await handle_pixhawk_data(data)
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"💥 Lỗi trong Pixhawk loop: {e}")


async def humminbird_loop():
    humminbird = await asyncio.to_thread(connect_humminbird)
    if humminbird is None:
        print("⛔ Không đọc được dữ liệu từ Humminbird.")
        return
    try:
        while True:
            nmea_line = await asyncio.to_thread(read_nmea, humminbird)
            if nmea_line:
                await handle_nmea_data(nmea_line)
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print("\n🛑 Ngắt luồng Humminbird.")
    except Exception as e:
        print(f"Lỗi trong humminbird_loop: {e}")

async def camera_loop():
    camera = USBCamera()
    while True:
        try:
            await asyncio.to_thread(camera.open)
            print("📷 Camera đã kết nối.")
            while True:
                frame = await asyncio.to_thread(camera.read_frame)
                await handle_camera_frame(frame)
        except Exception as e:
            print(f"💥 Lỗi camera: {e}")
            print("🔁 Thử kết nối lại camera sau 2 giây...")
            await asyncio.sleep(2)
        finally:
            await asyncio.to_thread(camera.release)
            await asyncio.sleep(1)

async def main_loop():
    tasks = [
        asyncio.create_task(start_web_server()),
        asyncio.create_task(pixhawk_loop()),
        asyncio.create_task(humminbird_loop()),
        asyncio.create_task(camera_loop()),
        asyncio.create_task(database_loop()),
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n🛑 Dừng toàn bộ chương trình.")
