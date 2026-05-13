#!/bin/bash

# Get list of packages in tracter_ws/src
PKGS=$(colcon list --base-paths tracter_ws/src --names-only)

if [ -z "$PKGS" ]; then
    echo "No packages found in tracter_ws/src"
    exit 1
fi

echo "Cleaning old build files for: $PKGS"
for pkg in $PKGS; do
    rm -rf "build/$pkg" "install/$pkg"
done

echo "Building only tracter packages: $PKGS"

# Perform colcon build for specific packages
colcon build --symlink-install \
    --packages-up-to $PKGS \
    --cmake-args \
    ' -DCMAKE_BUILD_TYPE=Release' \
    ' -DCMAKE_EXPORT_COMPILE_COMMANDS=1' \
    ' -GNinja' \
    ' -DCMAKE_CXX_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_C_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_CXX_FLAGS=-fdiagnostics-color' \
    --event-handlers console_cohesion+ \
    "$@"
