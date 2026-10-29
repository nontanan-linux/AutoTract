#!/usr/bin/env bash
# Goal: home (ID: 1) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 27525.28515625
    y: 15418.7822265625
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.8574305736145194
    w: 0.5145996613204057
'
