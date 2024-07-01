from copy import deepcopy
import pytest

from src.driver.driver_serial.serial_base import generate_crc
from src.driver.driver_serial.camera_serial.camera_serial_command import (
    ADDR,
    READ,
    WRITE,
    _build_command,
    _build_read_command,
    _build_write_command,
    get_ssid_command,
    set_ssid_command,
    get_password_command,
    set_password_command,
    parse_read_ack,
    parse_write_ack,
)

valid_ack_without_crc = [ADDR, READ, 2, 0x12, 0x34]
invalid_length_ack = [ADDR, READ, 3, 0x12, 0x34]
wrong_address_ack = [0x02, READ, 2, 0x12, 0x34, 0x7B, 0x8C]
wrong_command_ack = [ADDR, 0x04, 2, 0x12, 0x34, 0x7B, 0x8C]
wrong_crc_ack = [ADDR, READ, 2, 0x12, 0x34, 0x7B, 0x8D]


def test_build_command():
    addr = ADDR
    type_ = 0x03
    register_start = 0x1000
    data = [0x01, 0x02]
    expected_command = [ADDR, 0x03, 0x10, 0x00, 0x01, 0x02]
    expected_command.extend(generate_crc(expected_command))
    assert _build_command(addr, type_, register_start, data) == expected_command


def test_build_read_command():
    addr = ADDR
    register_start = 0x00
    length = 32
    expected_command = _build_command(ADDR, 0x03, register_start, [length])
    assert _build_read_command(register_start, length) == expected_command


def test_build_write_command():
    addr = 0x01
    register_start = 0x00
    write_data = [0x41, 0x42, 0x43]  # 'ABC' in ASCII
    expected_command = _build_command(ADDR, 0x06, register_start, [3, 0x41, 0x42, 0x43])
    assert _build_write_command(register_start, write_data) == expected_command


def test_get_ssid_command():
    assert get_ssid_command() == _build_read_command(0x00, 32)


def test_set_ssid_command():
    ssid = "TestSSID"
    ssid_list = [ord(char) for char in ssid.ljust(32, "\0")]
    expected_command = _build_write_command(0x00, ssid_list)
    assert set_ssid_command(ssid)[: len(expected_command)] == expected_command


def test_set_32_ssid_command():
    ssid = "1234567890ABCDEFGHIJKLMNOPQRSTUV"
    ssid_list = [ord(char) for char in ssid.ljust(32, "\0")]
    expected_command = _build_write_command(0x00, ssid_list)
    assert set_ssid_command(ssid)[: len(expected_command)] == expected_command


def test_get_password_command():
    assert get_password_command() == _build_read_command(0x20, 32)


def test_set_password_command():
    password = "TestPass"
    password_list = [ord(char) for char in password.ljust(32, "\0")]
    expected_command = _build_write_command(0x20, password_list)
    assert set_password_command(password)[: len(expected_command)] == expected_command


def test_set_32_password_command():
    password = "1234567890ABCDEFGHIJKLMNOPQRSTUV"
    password_list = [ord(char) for char in password.ljust(32, "\0")]
    expected_command = _build_write_command(0x20, password_list)
    assert set_password_command(password)[: len(expected_command)] == expected_command


def test_parse_read_ack_valid():
    valid_ack = deepcopy(valid_ack_without_crc)
    valid_ack.extend(generate_crc(valid_ack))
    assert parse_read_ack(valid_ack) == [
        0x12,
        0x34,
    ]


def test_parse_read_ack_invalid_length():
    assert parse_read_ack(invalid_length_ack) == []


def test_parse_read_ack_wrong_address():

    assert parse_read_ack(wrong_address_ack) == []


def test_parse_read_ack_wrong_command():
    assert parse_read_ack(wrong_command_ack) == []


def test_parse_read_ack_wrong_crc():
    assert parse_read_ack(wrong_crc_ack) == []


def test_parse_write_ack_valid():
    ack = deepcopy(valid_ack_without_crc)
    ack[1] = WRITE
    ack.extend(generate_crc(ack))
    assert parse_write_ack(ack)


def test_parse_write_ack_invalid_length():
    ack = deepcopy(invalid_length_ack)
    ack[1] = WRITE
    assert not parse_write_ack(ack)


def test_parse_write_ack_wrong_address():
    ack = deepcopy(wrong_address_ack)
    ack[1] = WRITE
    assert not parse_write_ack(ack)


def test_parse_write_ack_wrong_command():
    ack = deepcopy(wrong_command_ack)
    assert not parse_write_ack(ack)


def test_parse_write_ack_wrong_crc():
    ack = deepcopy(wrong_crc_ack)
    ack[1] = WRITE
    assert not parse_write_ack(ack)
