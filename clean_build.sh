#!/bin/bash

# Remove build, install, and log directories
rm -rf build install log

# Perform a clean build with colcon
colcon build --symlink-install \
    --cmake-args \
    ' -DCMAKE_BUILD_TYPE=Release' \
    ' -DCMAKE_EXPORT_COMPILE_COMMANDS=1' \
    ' -GNinja' \
    ' -DCMAKE_CXX_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_C_COMPILER_LAUNCHER=ccache' \
    ' -DCMAKE_CXX_FLAGS=-fdiagnostics-color' \
    --event-handlers console_cohesion+ \
    "$@"
