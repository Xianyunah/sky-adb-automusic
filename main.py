import os
import json
import time
import subprocess
import sys
from configparser import ConfigParser
from collections import defaultdict

CONFIG_FILE             = "config.ini"
DEFAULT_ADB_CMD         = "input tap"
DEFAULT_USE_WIRELESS    = "false"
DEFAULT_WIRELESS_IP     = "192.168.1.100"
DEFAULT_WIRELESS_PORT   = "5555"
BUSY_WAIT_THRESHOLD_MS  = 5

# 默认屏幕坐标映射
coords = [
    (900, 220), (1100, 220), (1280, 220), (1450, 220), (1650, 220),
    (900, 400), (1100, 400), (1280, 400), (1450, 400), (1650, 400),
    (900, 580), (1100, 580), (1280, 580), (1450, 580), (1650, 580),
]
DEFAULT_MAPPING = {}
for track in (1, 2):
    for i, (x, y) in enumerate(coords):
        DEFAULT_MAPPING[f"{track}Key{i}"] = (x, y)

def init_config():
    """首次运行时生成默认 config.ini 并退出。"""
    cfg = ConfigParser()
    cfg.optionxform = str  # 保留大小写
    cfg["Settings"] = {
        "adb_cmd":       DEFAULT_ADB_CMD,
        "use_wireless":  DEFAULT_USE_WIRELESS,
        "wireless_ip":   DEFAULT_WIRELESS_IP,
        "wireless_port": DEFAULT_WIRELESS_PORT,
    }
    cfg["KeyMapping"] = {
        key: f"{x},{y}" for key, (x, y) in DEFAULT_MAPPING.items()
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)
    print(f"[+] 已生成 `{CONFIG_FILE}`，请根据设备设置无线调试和屏幕坐标后重试。")
    exit(0)

def normalize_key(raw: str) -> str:
    """规范化键名，如 '1key3' → '1Key3'。"""
    low = raw.lower()
    if "key" in low:
        idx = low.index("key")
        return low[:idx] + "Key" + low[idx + 3:]
    return raw

def list_adb_devices():
    """列出当前连接的设备并返回列表。"""
    result = subprocess.run(
        ["adb", "devices"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    lines = result.stdout.splitlines()
    devices = []
    for line in lines[1:]:  # 第 1 行是标题
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])
    return devices

def select_device(devices):
    """让用户选择一个设备，并断开其他设备。"""
    print("\n检测到多个设备：")
    for idx, dev in enumerate(devices):
        print(f"[{idx}] {dev}")
    while True:
        try:
            choice = int(input("请选择要使用的设备编号："))
            if 0 <= choice < len(devices):
                break
        except ValueError:
            pass
        print("无效选择，请重试。")

    selected_device = devices[choice]
    print(f"[+] 选择设备：{selected_device}")
    for dev in devices:
        if dev != selected_device:
            print(f"[-] 断开设备：{dev}")
            subprocess.run(["adb", "disconnect", dev], stdout=subprocess.DEVNULL)

    return selected_device

def connect_wireless(ip: str, port: str):
    print(f"[+] 正在尝试无线连接到 {ip}:{port}...")
    result = subprocess.run(
        ["adb", "connect", f"{ip}:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if "connected to" in result.stdout:
        print(f"[+] 无线连接成功：{ip}:{port}")
    else:
        print(f"[!] 无线连接失败：{result.stdout.strip()}")

def load_config():
    """加载配置文件并返回配置值。"""
    if not os.path.exists(CONFIG_FILE):
        init_config()

    cfg = ConfigParser()
    cfg.optionxform = str  # 保留大小写
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg.read_file(f)

    settings = cfg["Settings"]
    adb_cmd   = settings.get("adb_cmd", DEFAULT_ADB_CMD)
    use_wireless = settings.get("use_wireless", DEFAULT_USE_WIRELESS).lower() == "true"
    wireless_ip   = settings.get("wireless_ip", DEFAULT_WIRELESS_IP)
    wireless_port = settings.get("wireless_port", DEFAULT_WIRELESS_PORT)

    if use_wireless:
        connect_wireless(wireless_ip, wireless_port)


    devices = list_adb_devices()
    if len(devices) > 1:
        select_device(devices)
    elif len(devices) == 0:
        raise ConnectionError("没有检测到任何设备，请检查连接状态。")

    mapping = {}
    for raw_key, raw_val in cfg["KeyMapping"].items():
        key = normalize_key(raw_key)
        try:
            x, y = map(int, raw_val.split(","))
        except ValueError:
            print(f"[!] 坐标解析失败：{raw_key} = {raw_val}，已设为 (0,0)")
            x, y = 0, 0
        mapping[key] = (x, y)

    return adb_cmd, mapping

def detect_skym_files():
    """检测当前目录中的 .skym 文件并让用户选择。"""
    files = [f for f in os.listdir('.') if f.endswith('.skym')]
    if not files:
        raise FileNotFoundError("当前目录没有 .skym 格式的乐谱文件！")
    
    print("\n检测到以下乐谱文件：")
    for idx, file in enumerate(files):
        print(f"[{idx}] {file}")
    while True:
        try:
            choice = int(input("请选择要播放的乐谱编号："))
            if 0 <= choice < len(files):
                break
        except ValueError:
            pass
        print("无效选择，请重试。")

    return files[choice]

def load_chart(path):
    """加载 .skym 或 .txt 格式的 JSON 谱面，返回第一个 chart 对象"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"谱面文件未找到：{path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 如果顶层是列表，就取第一个元素
    if isinstance(data, list):
        if not data:
            raise ValueError("谱面文件是空列表！")
        return data[0]
    # 否则直接返回（假定它就是 dict）
    return data


def busy_wait(ms: float):
    end = time.perf_counter() + ms / 1000
    while time.perf_counter() < end:
        pass

def play_low_latency(chart, adb_cmd, mapping):
    groups = defaultdict(list)
    times = []
    for note in chart["songNotes"]:
        t = note["time"]
        groups[t].append(note["key"])
        times.append(t)
    total_ms = max(times)

    proc = subprocess.Popen(
        ["adb", "shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True
    )

    start = time.perf_counter()
    for t in sorted(groups):
        elapsed = (time.perf_counter() - start) * 1000
        wait_ms = t - elapsed
        if wait_ms > 0:
            if wait_ms < BUSY_WAIT_THRESHOLD_MS:
                busy_wait(wait_ms)
            else:
                time.sleep(wait_ms / 1000)

        keys = groups[t]
        elapsed = (time.perf_counter() - start) * 1000
        pct     = elapsed / total_ms * 100
        sys.stdout.write(f"\r进度: {pct:6.2f}% | {int(elapsed):5d}/{total_ms}ms | keys: {','.join(keys)}")
        sys.stdout.flush()

        for k in keys:
            x, y = mapping.get(k, (0, 0))
            proc.stdin.write(f"{adb_cmd} {x} {y}\n")
        proc.stdin.flush()

    proc.stdin.close()
    proc.wait()
    print()



if __name__ == "__main__":
    while True:  # 主循环，支持用户选择重新播放乐谱
        try:
            # 加载配置
            adb_cmd, key_mapping = load_config()

            # 判断是否启用无线调试
            cfg = ConfigParser()
            cfg.optionxform = str
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.read_file(f)
            use_wireless = cfg["Settings"].get("use_wireless", "false").lower() == "true"
            if use_wireless:
                wireless_ip = cfg["Settings"].get("wireless_ip", DEFAULT_WIRELESS_IP)
                wireless_port = cfg["Settings"].get("wireless_port", DEFAULT_WIRELESS_PORT)
                connect_wireless(wireless_ip, wireless_port)

            # 让用户选择乐谱文件
            chart_file = detect_skym_files()
            chart = load_chart(chart_file)
            all_keys = {n["key"] for n in chart["songNotes"]}
            for k in all_keys:
                if k not in key_mapping:
                    print(f"[!] 配置缺失 {k}，已补齐为 (0,0)")
                    key_mapping[k] = (0, 0)

            print(f"\n曲目：{chart['name']}")
            print(f"路径：{os.path.abspath(chart_file)}")
            print("映射：", key_mapping)
            print("\n开始演奏...\n")
            play_low_latency(chart, adb_cmd, key_mapping)
            print("\n演奏结束！")

            # 用户确认是否退出或重新选择
            while True:
                user_choice = input("\n是否要退出程序？(输入 '是' 退出，输入 '否' 重新选择乐谱)：").strip().lower()
                if user_choice == "是":
                    print("已退出")
                    exit(0)
                elif user_choice == "否":
                    print("\n重新选择乐谱...")
                    break
                else:
                    print("无效输入，请输入 '是' 或 '否'。")

        except Exception as e:
            print(f"\n[!] 脚本错误：{e}")


