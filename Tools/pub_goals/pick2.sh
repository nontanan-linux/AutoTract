#!/usr/bin/env bash
# Goal: pick2 (ID: 4) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 28557.59765625
    y: 14152.2451171875
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.954909612066721
    w: 0.296896670211347
'
