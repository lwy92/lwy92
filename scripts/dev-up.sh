#!/usr/bin/env bash
set -euo pipefail
cd deploy
docker compose up -d --build
