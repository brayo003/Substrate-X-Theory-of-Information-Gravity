#!/usr/bin/env bash
pkill ollama || true
sleep 1
nohup ollama serve > ollama.log 2>&1 &
sleep 3
python3 ollama_healthcheck.py
