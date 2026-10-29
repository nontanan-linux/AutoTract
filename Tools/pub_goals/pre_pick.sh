#!/usr/bin/env bash
# Goal: pre-pick (ID: 2) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 28553.16796875
    y: 14153.1767578125
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.8879284788610585
    w: 0.4599815392246593
'
