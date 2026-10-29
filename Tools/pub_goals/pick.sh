#!/usr/bin/env bash
# Goal: pick (ID: 3) | Type: station

ros2 topic pub --once /planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: 28545.630859375
    y: 14161.638671875
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.9434781107263811
    w: 0.3314348421336818
'
