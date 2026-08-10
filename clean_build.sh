#!/bin/bash

# Source environment setup if exists
if [ -f "$(dirname "$0")/tracter.env" ]; then
    source "$(dirname "$0")/tracter.env"
fi

# Remove build, install, and log directories

#rm -rf build install log

ccache -C

# Perform a clean build with colcon
colcon build --symlink-install \
    --parallel-workers 1 \
    --cmake-args \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=1 \
    -GNinja \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
    -DCMAKE_C_COMPILER_LAUNCHER=ccache \
    -DCMAKE_CXX_FLAGS="-Wno-error=maybe-uninitialized -Wno-error=uninitialized -Wno-error=narrowing"\
    --event-handlers console_cohesion+ \
    --packages-skip autoware_tensorrt_bevformer \
    "$@"
