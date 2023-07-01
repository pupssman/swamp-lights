reqs:
	pip install -r requirements.txt

# this is to flash esp8266 fw
flash_8266:
	esptool.py --chip esp8266 --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 esp8266-20230426-v1.20.0.bin

# this is to flash a esp32 fw
flash_32:
	esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin
