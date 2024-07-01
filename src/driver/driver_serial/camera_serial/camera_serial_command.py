from src.driver.driver_serial.serial_base import generate_crc

ADDR = 1

READ = 0x03
WRITE = 0x06


def _build_command(addr, type, register_start, data):
    command = [addr, type, (register_start >> 8) & 0xFF, register_start & 0xFF]
    command.extend(data)
    command.extend(generate_crc(command))
    return command


def _build_read_command(register_start, length):
    return _build_command(ADDR, READ, register_start, [length])


def _build_write_command(register_start, write_data):
    data_to_send = [len(write_data)] + write_data
    return _build_command(ADDR, WRITE, register_start, data_to_send)


def get_ssid_command():
    return _build_read_command(0x00, 32)


def set_ssid_command(ssid):
    ssidList = []
    for i in range(32):
        if i < len(ssid):
            ssidList.append(ord(ssid[i]))
        else:
            ssidList.append(0)
    return _build_write_command(0x00, ssidList)


def get_password_command():
    return _build_read_command(0x20, 32)


def set_password_command(password):
    passwordList = []
    for i in range(32):
        if i < len(password):
            passwordList.append(ord(password[i]))
        else:
            passwordList.append(0)
    return _build_write_command(0x20, passwordList)


def set_wifi_enable_command():
    return _build_write_command(0x40, 1)


def get_wifi_enable_command():
    return _build_read_command(0x40, 1)


def get_wifi_connect_status_command():
    return _build_read_command(0x41, 1)


def parse_read_ack(ack):
    length = ack[2]
    if (
        len(ack) > 5
        and ack[0] == ADDR
        and ack[1] == READ
        and length == len(ack) - 5
        and ack[-2:] == generate_crc(ack[:-2])
    ):
        data = []
        for i in range(ack[2]):
            data.append(ack[3 + i])
        return data
    return []


def parse_write_ack(ack):
    length = ack[2]
    if (
        len(ack) > 5
        and ack[0] == ADDR
        and ack[1] == WRITE
        and length == len(ack) - 5
        and ack[-2:] == generate_crc(ack[:-2])
    ):
        return True
    return False
