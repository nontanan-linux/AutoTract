#!/bin/bash

# 1. ค้นหาแพ็กเกจฝั่งรถแทรกเตอร์ (ขยายผลการค้นหาให้ลึกขึ้นโดยการปล่อยพาร์ทอิสระ)
PKGS=$(colcon list --base-paths tracter_ws --names-only)

if [ -z "$PKGS" ]; then
    echo "No packages found in tracter_ws"
    exit 1
fi

echo "Cleaning old build files for: $PKGS"
for pkg in $PKGS; do
    rm -rf "build/$pkg" "install/$pkg"
done

# ล้างเผื่อโฟลเดอร์หลักกรณีชื่อไม่ตรงในลิสต์
rm -rf "build/carla_msgs" "install/carla_msgs"

echo "Building tracter packages with deep path scan..."

# 2. ทำการบิวด์โดยระบุให้ Colcon สแกนทั้งพื้นที่ และเลือกเจาะจงรายชื่อกลุ่มแทรกเตอร์ พ่วง carla_msgs
colcon build --symlink-install \
    --packages-select $PKGS \
    --parallel-workers 1 \
    # --packages-up-to pcl_recorder \
    --cmake-args \
    ' -DCMAKE_BUILD_TYPE=Release' \
    ' -DCMAKE_EXPORT_COMPILE_COMMANDS=1' \
    ' -GNinja' \
    ' -DCMAKE_CXX_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_C_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_CXX_FLAGS=-fdiagnostics-color' \
    --event-handlers console_cohesion+ \
    # --packages-up-to pcl_recorder
    "$@"
