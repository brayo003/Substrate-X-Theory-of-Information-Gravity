#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$ROOT_DIR/engine"
BUILD_DIR="$ROOT_DIR/build"

mkdir -p "$ENGINE_DIR" "$BUILD_DIR"

cd "$ENGINE_DIR"

if [ ! -d chocolate-doom ]; then
    git clone https://github.com/chocolate-doom/chocolate-doom.git
fi

cd chocolate-doom

./autogen.sh
./configure --prefix="$BUILD_DIR"
make -j$(nproc)
make install

echo "Chocolate Doom built into $BUILD_DIR"
