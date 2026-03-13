#!/usr/bin/env bash

echo "[1] Killing ALL ollama processes (root + user)"
sudo pkill ollama || true
pkill ollama || true

sleep 2

echo "[2] Starting ollama as USER (no sudo)"
nohup ollama serve > ollama.log 2>&1 &

echo "[3] Waiting for socket readiness"
for i in {1..10}; do
  sleep 1
  curl -s http://127.0.0.1:11434/api/version && break
done

echo "[4] Running healthcheck"
python3 ollama_healthcheck.py
