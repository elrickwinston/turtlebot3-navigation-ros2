# TurtleBot3 Sensor-Based Navigation and Visual Perception Pipeline

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/Python-3.10-green)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)](https://opencv.org/)

A ROS2-based autonomous navigation and visual perception project developed 
at Ravensburg-Weingarten University of Applied Sciences (RWU), Germany. 
The project uses TurtleBot3 in Gazebo simulation to implement wall following, 
SLAM-based mapping, autonomous goal navigation and camera-based visual 
perception for line following and obstacle avoidance in the RWU Autorace arena.

---

## Table of Contents

- [Overview](#overview)
- [Project Stages](#project-stages)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Package Structure](#package-structure)
- [How to Run](#how-to-run)
- [Key Concepts](#key-concepts)
- [Results](#results)
- [University](#university)

---

## Overview

This project was developed as part of the Autonomous Robots course at RWU. 
It covers the full pipeline from basic ROS2 fundamentals to autonomous 
navigation and visual perception on a real robot simulation environment.

The robot uses:
- **LiDAR** (`/scan` topic) for wall detection and distance measurement
- **Camera** (`/camera/image_raw`) for road line detection and sign recognition
- **Nav2 + Cartographer** for SLAM-based autonomous navigation
- **OpenCV** for image processing and visual perception

---

## Project Stages

### Stage 1 — Python and ROS2 Fundamentals

**Laser Scan Processing:**
- Procedural approach — reading laser range values with simple functions
- Object-oriented approach — same logic encapsulated in a Python class

**ROS2 Basics:**
- Running `ros2 node list`, `ros2 topic list`, `ros2 topic echo`
- Understanding publisher/subscriber communication model
- Turtlesim exercises — moving turtle, spawning second turtle

### Stage 2 — ROS2 Node Development

**Publisher/Subscriber Stack:**
- Package `py_pubsub` — publishes `Hello World: N` every 0.5 seconds
- Subscriber prints received messages

**Turtlesim Control:**
- Package `turtlemover` — drives turtle in circles
- Subscriber counts circles by detecting when turtle crosses starting angle
- Node `move_turtle_topic` — drives exactly N circles then stops

**Catch a Turtle:**
- Package `catch_a_turtle` with two nodes
- `turtle_runner` moves turtle1 in circles
- `catch_a_turtle` node calculates distance between turtle1 and turtle2
- Drives turtle2 toward turtle1, stops and prints "Caught!" when distance < 0.5

### Stage 3  — TurtleBot3 Navigation

**Drive to Wall:**
- Package `drive_to_wall`, node `drive_to_wall_node`
- Reads `/scan` topic — uses `ranges[0]` for front distance
- Drives at `linear.x = 0.5`, stops when front distance < 1.0m

**Wall Follower:**
- Package `follow_wall`, node `follow_wall_node`
- State machine: `FORWARD → TURNING → WAIT → FOLLOW`
- Front sensor: `min(ranges[0], ranges[5], ranges[355])`
- Right sensors: `ranges[260]`, `ranges[280]`
- TURNING: `angular.z = 0.5` until aligned
- FOLLOW: proportional control based on right sensor average
- Tested with obstacles — existing state machine handled them correctly

**SLAM Mapping + Nav2:**
- Built map using Cartographer SLAM while driving with wall follower
- Saved map using `map_saver_cli`
- Loaded map in Nav2 for autonomous navigation
- Set 2D Pose Estimate for AMCL localisation
- Package `my_nav2`, node `goal_pub` — publishes random goals every 15 seconds

### Stage 4  — RWU Autorace Arena (In Progress)

**Wall Following in Tunnel :**
- Existing `follow_wall_node` worked in tunnel
- Robot navigated tunnel sections successfully

**Line Following :**
- Package `my_cv_package`, node `cv_view` — camera feed visualization
- Node `cv_color_detect` — detects white and yellow lines using HSV masking
- Package `follow_line`, node `follow_line_node`
- White line HSV range: `[0,0,180]` to `[180,50,255]`
- Yellow line HSV range: `[20,100,100]` to `[30,255,255]`
- Bottom quarter ROI for performance
- Centroid method: `cx = M['m10'] / M['m00']`
- Proportional control: `angular.z = 0.005 * error`, clipped to `[-0.8, 0.8]`

**Obstacle Avoidance :**
- 3-state machine: `FOLLOW_LINE → FOLLOW_YELLOW → REALIGN`
- Switches to yellow line when obstacle detected at front < 0.5m
- Returns to white line after 150 frames
- REALIGN: rotates to reacquire white line

**Avoid Obstacles  — In Progress:**
- Robot needs to navigate around boxes on track
- Stop when white line reacquired
- Rotate 90° to continue line following

**Enter Tunnel  — In Progress:**
- Detect tunnel sign using OpenCV
- Drive forward until inside tunnel using laser sensor

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| ROS2 | Humble | Robot middleware |
| Python | 3.10 | Node development |
| OpenCV | 4.x | Visual perception |
| Gazebo | 11 | Robot simulation |
| RViz2 | 11 | Visualisation |
| Nav2 | Humble | Autonomous navigation |
| Cartographer | 2.x | SLAM mapping |
| TurtleBot3 | Waffle Pi | Robot platform |

---

## System Requirements

- Ubuntu 22.04
- ROS2 Humble
- TurtleBot3 packages
- OpenCV Python (`pip install opencv-python`)
- Gazebo 11

---

## Package Structure

ros2_ws/
└── src/
├── py_pubsub/ # Stage 2 — publisher/subscriber
├── turtlemover/ # Stage 2 — turtlesim control
├── catch_a_turtle/ # Stage 2 — turtle chasing
├── drive_to_wall/ # Stage 3 — wall detection
├── follow_wall/ # Stage 3 — wall following state machine
├── my_nav2/ # Stage 3 — autonomous goal navigation
├── my_cv_package/ # Stage 4 — camera visualization + color detection
└── follow_line/ # Stage 4 — line following + obstacle avoidance


---

## How to Run

### Setup
```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
```

### Stage 3 — Wall Follower
```bash
# Terminal 1 — Launch Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage1.launch.py

# Terminal 2 — Run wall follower
ros2 run follow_wall follow_wall_node
```

### Stage 3 — SLAM Mapping
```bash
# Terminal 1 — Launch Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage4.launch.py use_sim_time:=True

# Terminal 2 — Start Cartographer
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

# Terminal 3 — Drive robot to build map
ros2 run follow_wall follow_wall_node

# Terminal 4 — Save map when done
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/maps/myfirstmap
```

### Stage 3 — Nav2 Autonomous Navigation
```bash
# Terminal 1 — Launch Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage4.launch.py use_sim_time:=True

# Terminal 2 — Start Nav2
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  map:=~/ros2_ws/maps/myfirstmap.yaml use_sim_time:=True

# Terminal 3 — Publish random goals
ros2 run my_nav2 goal_pub
```

### Stage 4 — Line Following
```bash
# Terminal 1 — Launch Autorace arena
ros2 launch tb3_rwu_arena tb3_sim.launch.py x:=0.82 y:=-1.75 yaw:=0.0

# Terminal 2 — Run line follower
ros2 run follow_line follow_line_node
```

### Stage 4 — Obstacle Avoidance
```bash
# Terminal 1 — Launch Autorace arena
ros2 launch tb3_rwu_arena tb3_sim.launch.py x:=1.71 y:=0.39 yaw:=1.57

# Terminal 2 — Run obstacle avoidance
ros2 run follow_line follow_line_node
```

---

## Key Concepts

### State Machine Navigation
The wall follower uses a 4-state machine:

FORWARD → drives straight until obstacle detected at front
TURNING → rotates left until aligned with wall
WAIT → waits 2.5 seconds for stabilisation
FOLLOW → follows wall using proportional control on right sensors


### HSV Colour Detection
HSV (Hue, Saturation, Value) is used instead of RGB because:
- Hue stays consistent under different lighting conditions
- White detection: low saturation, high value
- Yellow detection: hue range 20-30, high saturation

### Centroid-Based Line Following
```python
M = cv2.moments(roi)
cx = M['m10'] / M['m00']          # centroid x position
error = img_center_x - cx          # deviation from centre
angular.z = 0.005 * error          # proportional control
```

### SLAM — Simultaneous Localisation and Mapping
- Robot builds a map while navigating unknown environment
- Cartographer uses LiDAR scan data to create occupancy grid map
- AMCL localises robot on saved map for Nav2 navigation

---

## Results

| Stage | Task | Status |
|---|---|---|
| 1 | Laser scan processing | Complete |
| 2 | Publisher/Subscriber nodes | Complete |
| 2 | Catch a turtle | Complete |
| 3 | Wall follower | Complete |
| 3 | SLAM mapping | Complete |
| 3 | Nav2 navigation | Complete |
| 4 | Wall following in tunnel | Complete |
| 4 | Line following | Complete |
| 4 | Obstacle avoidance | Complete |
| 4 | Avoid obstacles task | In Progress |
| 4 | Enter tunnel | In Progress |

---

## University

**Ravensburg-Weingarten University of Applied Sciences (RWU)**  
M.Sc. Mechatronics — Autonomous Robots Course
Weingarten, Germany
