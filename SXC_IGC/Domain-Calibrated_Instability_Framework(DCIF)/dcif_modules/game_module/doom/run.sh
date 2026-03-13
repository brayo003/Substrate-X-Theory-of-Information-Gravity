#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$ROOT_DIR/build/bin/chocolate-doom"
IWAD_DIR="$ROOT_DIR/iwads"

export DOOMWADDIR="$IWAD_DIR"

exec "$BIN" -iwad "$IWAD_DIR/DOOM1.WAD"
