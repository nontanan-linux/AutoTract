#!/usr/bin/env bash
# Goal: drop (ID: 6) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 27483.0703125
    y: 15479.212890625
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.8612997255433853
    w: 0.5080972178421068
'
