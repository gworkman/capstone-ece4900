flash3:
	esptool.py --port $(port) --baud 115200 erase_flash
	esptool.py --chip esp32 --port $(port) --baud 115200 write_flash -z 0x1000 firmware-3.bin

flash4:
	esptool.py --port $(port) --baud 115200 erase_flash
	esptool.py --chip esp32 --port $(port) --baud 115200 write_flash -z 0x1000 firmware-4.bin

flash: flash4

put:
	ampy --port $(port) put $(file)

show:
	ampy --port $(port) get $(file)

list:
	ampy --port $(port) ls

restart:
	ampy --port $(port) reset
