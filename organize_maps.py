import os
import shutil

base_dir = "/home/tacv/AutoTract"
hdmaps_dir = os.path.join(base_dir, "carla", "HDMaps")
autoware_contents_dir = os.path.join(base_dir, "op_agent", "autoware-contents")
osm_dir = os.path.join(autoware_contents_dir, "maps", "vector_maps", "lanelet2")

# List of towns to organize
towns = ["Town01", "Town02", "Town03", "Town04", "Town05", "Town06", "Town07"]

for town in towns:
    town_folder = os.path.join(hdmaps_dir, town)
    os.makedirs(town_folder, exist_ok=True)
    
    # 1. Move and rename PCD file from HDMaps/TownXX.pcd to HDMaps/TownXX/pointcloud_map.pcd
    pcd_src = os.path.join(hdmaps_dir, f"{town}.pcd")
    pcd_dst = os.path.join(town_folder, "pointcloud_map.pcd")
    if os.path.exists(pcd_src):
        shutil.move(pcd_src, pcd_dst)
        print(f"Moved: {pcd_src} -> {pcd_dst}")
    else:
        if os.path.exists(pcd_dst):
            print(f"Info: {pcd_dst} is already in place.")
        else:
            print(f"Warning: {pcd_src} not found.")
        
    # 2. Copy and rename OSM file from autoware-contents to HDMaps/TownXX/lanelet2_map.osm
    osm_src = os.path.join(osm_dir, f"{town}.osm")
    osm_dst = os.path.join(town_folder, "lanelet2_map.osm")
    if os.path.exists(osm_src):
        shutil.copy2(osm_src, osm_dst)
        print(f"Copied: {osm_src} -> {osm_dst}")
    else:
        if os.path.exists(osm_dst):
            print(f"Info: {osm_dst} is already in place.")
        else:
            print(f"Warning: {osm_src} not found.")
        
    # 3. Create map_projector_info.yaml in the town folder
    yaml_path = os.path.join(town_folder, "map_projector_info.yaml")
    with open(yaml_path, "w") as f:
        f.write("projector_type: local\n")
    print(f"Created: {yaml_path}")

print("\nMap organization completed successfully!")
