#!/usr/bin/env bash
# Goal: weight (ID: 4) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 28669.025390625
    y: 14074.6533203125
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: -0.30408045561351
    w: 0.952646354380197
'
