#!/usr/bin/env python3

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil

CONNECTION = "tcp:127.0.0.1:5762"

SOURCE_SYSTEM = 1
SOURCE_COMPONENT = 211

START_AI_VISION = 31012
STOP_AI_VISION = 31013


master = mavutil.mavlink_connection(
    CONNECTION,
    source_system=SOURCE_SYSTEM,
    source_component=SOURCE_COMPONENT
)

print("==============================================")
print(" Fake AI Vision ACK")
print("==============================================")
print("AI identity : 1:211")

# 先送 Heartbeat，讓 ArduPilot 將 SERIAL1 / AI channel 標記為 active
master.mav.heartbeat_send(
    mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
    mavutil.mavlink.MAV_AUTOPILOT_INVALID,
    0,
    0,
    mavutil.mavlink.MAV_STATE_ACTIVE
)

print("Heartbeat sent")
print("Waiting for START/STOP AI VISION ...")
print()

while True:
    msg = master.recv_match(type="COMMAND_LONG", blocking=True)

    if msg.command not in (START_AI_VISION, STOP_AI_VISION):
        continue

    if msg.command == START_AI_VISION:
        print(
            f"START received | "
            f"mode={msg.param1:.0f} "
            f"stream={msg.param2:.0f} "
            f"freq={msg.param3:.1f}"
        )
    else:
        print("STOP received")

    master.mav.command_ack_send(
        msg.command,
        mavutil.mavlink.MAV_RESULT_ACCEPTED,
        0,
        0,
        1,
        1
    )

    print(f"ACK ACCEPTED sent | command={msg.command}")
