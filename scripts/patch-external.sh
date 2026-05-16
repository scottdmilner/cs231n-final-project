#!/bin/bash

set -e

ROOT_DIR=$(git rev-parse --show-toplevel)

if [ -f "${ROOT_DIR}/external/patches/openvdb.patch" ] && [ -d "${ROOT_DIR}/external/openvdb" ]; then
    cd "${ROOT_DIR}/external/openvdb"
    git apply --check ../patches/openvdb.patch 2>/dev/null && \
        git apply ../patches/openvdb.patch
    cd - > /dev/null
fi
