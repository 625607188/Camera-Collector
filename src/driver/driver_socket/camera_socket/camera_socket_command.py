import json
import hashlib


def generate_md5(src):
    md5_hash = hashlib.md5()
    md5_hash.update(src)
    return md5_hash.hexdigest()


def build_get_request(url) -> str:
    return f"GET {url} HTTP/1.1\r\n\r\n"


def build_post_request_json(url, data) -> str:
    json_data = json.dumps(data)
    return (
        f"POST {url} HTTP/1.1\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(json_data)}\r\n"
        "\r\n"
        f"{json_data}\r\n"
    )


def build_post_request_stream(url, data) -> str:
    md5_sum = generate_md5(data)
    return (
        f"POST {url} HTTP/1.1\r\n"
        "Content-Type: application/octet-stream\r\n"
        f"Content-Length: {len(data)}\r\n"
        f"Content-MD5: {md5_sum}\r\n"
        "\r\n"
        f"{data}"
    )

def ping_camera() -> str:
    return build_get_request("/camera/ping")

def get_camera_config() -> str:
    return build_get_request("/camera/config")


def set_camera_config(config) -> str:
    return build_post_request_json("/camera/config", json.dumps(config))


def control_camera(command) -> str:
    return build_post_request_json("/camera/control", json.dumps(command))


def upgrade_camera(file) -> str:
    return build_post_request_stream("/camera/upgrade", file)
