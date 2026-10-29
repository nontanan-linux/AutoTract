import csv
import os
from pathlib import Path


def generate_goal_scripts(
    csv_file_path: str = "/home/tacv/autoware_map/chememan_global/GoalPoints.csv",
    output_dir: str = "pub_goals",
    use_once_flag: bool = True,
) -> None:
    """Read goal points from a CSV file and save executable ROS 2 publish

    scripts inside the specified output directory.

    :param csv_file_path: Path to the input CSV file.
    :param output_dir: Directory where shell scripts will be stored (defaults
    to 'pub_goals').
    :param use_once_flag: If True, adds '--once' to avoid publishing
    continuously.
    """
    csv_path = Path(csv_file_path)
    out_dir = Path(output_dir)

    # Create the output directory if it does not exist
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    # ROS 2 publisher flag: '--once' publishes a single message and terminates
    once_flag = "--once " if use_once_flag else ""

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_name = row["name"].strip()

            # Sanitize filename: replace hyphens with underscores (e.g., pre-pick -> pre_pick.sh)
            clean_name = raw_name.replace("-", "_")
            script_filename = f"{clean_name}.sh"
            script_path = out_dir / script_filename

            # Convert coordinate and quaternion values to float
            x = float(row["x"])
            y = float(row["y"])
            z = float(row["z"])
            qx = float(row["qx"])
            qy = float(row["qy"])
            qz = float(row["qz"])
            qw = float(row["qw"])

            # Construct shell script content
            script_content = f"""#!/usr/bin/env bash
# Goal: {raw_name} (ID: {row['id']}) | Type: {row.get('node_type', '')}

ros2 topic pub {once_flag}/planning/mission_planning/goal geometry_msgs/msg/PoseStamped 'header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: "map"
pose:
  position:
    x: {x}
    y: {y}
    z: {z}
  orientation:
    x: {qx}
    y: {qy}
    z: {qz}
    w: {qw}
'
"""

            # Save file inside the output directory
            with open(script_path, mode="w", encoding="utf-8") as script_file:
                script_file.write(script_content)

            # Grant executable permissions (chmod +x)
            script_path.chmod(script_path.stat().st_mode | 0o111)

            print(f"Generated: {script_path}")


if __name__ == "__main__":
    generate_goal_scripts()
