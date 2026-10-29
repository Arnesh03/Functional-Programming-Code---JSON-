#!/usr/bin/env bash
# Put this project on the GPU box and run it there.
#
# Authentication is SSH keys only — this script never sees or asks for a password. Install the
# key once with:
#     ssh-copy-id -i ~/.ssh/id_ed25519.pub arnesh@172.25.0.179
#
# Usage:
#     scripts/deploy_gpu.sh inspect     # what is on the box, and what is in $HOME (reads only)
#     scripts/deploy_gpu.sh push        # copy the project across
#     scripts/deploy_gpu.sh setup       # build the venv and install requirements
#     scripts/deploy_gpu.sh run 20      # batch-run N samples there
#     scripts/deploy_gpu.sh pull        # bring results/ back
#
# Deliberately NOT in this script: deleting anything under $HOME. See `inspect` first — the
# delete list should be read by a human before it runs, once, and not live in a script that
# gets re-run.
set -euo pipefail

HOST="${GPU_HOST:-arnesh}"                  # ~/.ssh/config entry -> 172.25.0.179
REMOTE_DIR="${GPU_DIR:-~/nested_code}"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ssh_do() { ssh -o BatchMode=yes "$HOST" "$@"; }

case "${1:-}" in
inspect)
    echo "== host =="
    ssh_do 'hostname; uname -srm; nproc; free -g 2>/dev/null | head -2'
    echo; echo "== gpus =="
    ssh_do 'nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv 2>/dev/null || echo "no nvidia-smi"'
    echo; echo "== python =="
    ssh_do 'for p in python3 python3.12 python3.11 uv; do command -v $p >/dev/null && echo -n "$p: " && $p --version 2>&1 | head -1; done'
    echo; echo "== ollama on the box? =="
    ssh_do 'command -v ollama >/dev/null && ollama list 2>/dev/null | head -5 || echo "ollama not installed"'
    echo; echo "== disk =="
    ssh_do 'df -h ~ | tail -1'
    echo; echo "== what is under \$HOME (nothing is deleted by this command) =="
    ssh_do 'cd ~ && du -sh .[!.]* * 2>/dev/null | sort -h | tail -40; echo; echo "total:"; du -sh ~ 2>/dev/null'
    ;;
push)
    echo "Copying project -> $HOST:$REMOTE_DIR"
    ssh_do "mkdir -p $REMOTE_DIR"
    rsync -az \
        --exclude '.git' --exclude '.venv' --exclude '__pycache__' \
        --exclude 'results' --exclude 'logs' --exclude '*.db' \
        --exclude 'data/nested_code/py150.tar.gz' \
        "$LOCAL_DIR/app" "$LOCAL_DIR/scripts" "$LOCAL_DIR/assets" "$LOCAL_DIR/data" \
        "$LOCAL_DIR/webapp" "$LOCAL_DIR/main.py" "$LOCAL_DIR/requirements.txt" "$LOCAL_DIR/README.md" \
        "$HOST:$REMOTE_DIR/"
    echo "done"
    ;;
setup)
    ssh_do "cd $REMOTE_DIR && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && \
            .venv/bin/pip install -q python-dotenv && echo 'venv ready:' && .venv/bin/python --version"
    ;;
run)
    N="${2:-20}"
    STRATEGY="${3:-multicall}"
    echo "Running $N samples on $HOST (strategy=$STRATEGY)"
    ssh_do "cd $REMOTE_DIR && LLM_BACKEND=\${LLM_BACKEND:-ollama} \
            OLLAMA_HOST=\${OLLAMA_HOST:-http://localhost:11434} \
            .venv/bin/python scripts/run_code_pipeline.py --count $N --strategy $STRATEGY"
    ;;
pull)
    mkdir -p "$LOCAL_DIR/results"
    rsync -az "$HOST:$REMOTE_DIR/results/" "$LOCAL_DIR/results/"
    echo "results pulled into $LOCAL_DIR/results"
    ;;
*)
    sed -n '2,20p' "$0"
    exit 1
    ;;
esac
