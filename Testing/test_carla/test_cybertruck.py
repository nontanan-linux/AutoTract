#!/usr/bin/env python3
"""
CARLA Custom Vehicle Test Script
Generated: June 2026
Description: Spawns the custom Cybertruck blueprint, lifts its spawn point 
             to prevent falling through the ground, engages autopilot, and 
             warps the simulator spectator camera directly to the vehicle.
"""

import carla
import random
import time

def main():
    # 1. Connect to the CARLA Server
    print("Connecting to CARLA Server...")
    client = carla.Client('localhost', 2000)
    client.set_timeout(15.0)
    world = client.get_world()

    # 2. Retrieve Blueprint Library
    blueprint_library = world.get_blueprint_library()
    
    # Matches the exact identifier specified in your package.json registration
    blueprint_id = 'vehicle.tesla.cybertruck'
    cybertruck_bp = blueprint_library.find(blueprint_id)

    if cybertruck_bp is None:
        print(f"Error: '{blueprint_id}' could not be found in the CARLA library.")
        print("Please verify your package.json setup and check available vehicles using:")
        print("python3 config.py --list")
        return

    # 3. Handle Spawn Point Selection
    spawn_points = world.get_map().get_spawn_points()
    if not spawn_points:
        print("Error: No valid spawn points found on the current map.")
        return
    
    spawn_point = random.choice(spawn_points)
    
    # Critical Fix: Elevate Z-axis slightly to ensure custom physics meshes 
    # don't clip through the road surface on the first frame.
    spawn_point.location.z += 2.0 
    
    # 4. Spawn the Actor
    print(f"Attempting to spawn Cybertruck at Location: {spawn_point.location}")
    vehicle = world.spawn_actor(cybertruck_bp, spawn_point)

    try:
        # 5. Warp Simulator Spectator Camera to Vehicle
        print("Warping spectator camera to vehicle location...")
        time.sleep(0.5)  # Allow half a second for physics registration
        
        spectator = world.get_spectator()
        vehicle_transform = vehicle.get_transform()
        
        # Position camera slightly behind (-5m offset) and above (+3m offset) the car
        camera_location = vehicle_transform.location + carla.Location(z=3.0) - (vehicle_transform.get_forward_vector() * 5.0)
        camera_rotation = vehicle_transform.rotation
        camera_rotation.pitch = -20.0  # Angle the camera downwards slightly
        
        spectator.set_transform(carla.Transform(camera_location, camera_rotation))

        # 6. Engage Autopilot Controls
        vehicle.set_autopilot(True)
        print("\n========================================================")
        print(" Cybertruck spawned successfully and Autopilot is active!")
        print(" Check your CARLA Simulator window to watch it drive.")
        print(" Press Ctrl+C in this terminal to safely destroy actor.")
        print("========================================================\n")
        
        # Keep process alive to sustain actor lifecycle
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        # 7. Safe Resource Cleanup
        if 'vehicle' in locals() and vehicle is not None:
            print("Cleaning up... Destroying Cybertruck actor.")
            vehicle.destroy()
            print("Actor destroyed successfully.")

if __name__ == '__main__':
    main()
