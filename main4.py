import asyncio
from bleak import BleakClient, BleakScanner
import device_model
import logging

# 设置日志格式
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 蓝牙设备的MAC地址列表
MAC_ADDRESSES = ["CF:E2:17:57:36:B9"]

# 数据更新回调函数
def updateData(DeviceModel):
    logging.info(f"Updated data: {DeviceModel.deviceData}")

# 异步连接设备
async def connect_device(mac_address):
    while True:
        logging.info(f"Attempting to connect to {mac_address}...")
        try:
            # 扫描设备
            device = await BleakScanner.find_device_by_address(mac_address, timeout=15)
            if device:
                logging.info(f"Device found: {mac_address}")
                ble_device = device_model.DeviceModel("MyBle5.0", device, updateData)

                # 打开设备并建立连接
                await ble_device.openDevice()
                logging.info(f"Connected to {mac_address}")

                # 创建一个事件，用于处理断连后退出阻塞
                disconnect_event = asyncio.Event()

                # 创建BleakClient并设置断连回调
                async with BleakClient(device) as client:
                    client.set_disconnected_callback(
                        lambda _: disconnect_event.set()
                    )
                    try:
                        # 等待断连事件触发
                        await disconnect_event.wait()
                        logging.warning(f"Device {mac_address} disconnected.")
                    except asyncio.CancelledError:
                        logging.info(f"Connection to {mac_address} cancelled.")
            else:
                logging.warning(f"Device {mac_address} not found, retrying...")
        except Exception as ex:
            logging.warning(f"Failed to connect to {mac_address}: {ex}")
        finally:
            # 确保扫描间隔，避免蓝牙资源过度使用
            await asyncio.sleep(3)

# 主函数
async def main():
    tasks = [asyncio.create_task(connect_device(mac)) for mac in MAC_ADDRESSES]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
