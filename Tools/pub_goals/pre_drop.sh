#!/usr/bin/env bash
# Goal: pre-drop (ID: 5) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 27495.9375
    y: 15462.5673828125
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.9138948107963974
    w: 0.40595107439125805
'
