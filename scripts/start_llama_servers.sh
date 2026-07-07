#!/bin/bash
# Start both llama-server instances on AGX Thor.
# Run this on Thor (not on your local machine).
#
# Usage:
#   ./scripts/start_llama_servers.sh
#   ./scripts/start_llama_servers.sh stop

set -e

MODELS_DIR="${MODELS_DIR:-/workspace/Documents/models/GGUF}"

# === Main: Qwen3-VL-30B-A3B-Instruct (Q8_0 + mmproj) ===
MAIN_MODEL="$MODELS_DIR/Qwen3-VL-30B-A3B-Instruct-GGUF/Qwen3VL-30B-A3B-Instruct-Q8_0.gguf"
MAIN_MMPROJ="$MODELS_DIR/Qwen3-VL-30B-A3B-Instruct-GGUF/mmproj-Qwen3VL-30B-A3B-Instruct-F16.gguf"

# === Helper: Qwen-AgentWorld-35B-A3B (UD-Q4_K_M) ===
AGENT_WORLD_MODEL="$MODELS_DIR/Qwen-AgentWorld-35B-A3B-UD-Q4_K_M.gguf"

LOG_DIR="${LOG_DIR:-/tmp/llama-servers}"
mkdir -p "$LOG_DIR"

start_server() {
    local name="$1"
    local model="$2"
    local port="$3"
    local extra_args="$4"
    local log="$LOG_DIR/${name}.log"

    if [ ! -f "$model" ]; then
        echo "ERROR: model not found: $model"
        return 1
    fi

    # Check if port already in use
    if lsof -i ":$port" 2>/dev/null | grep -q LISTEN; then
        echo "Port $port already in use (server might be running). Skipping $name."
        return 0
    fi

    echo "Starting $name on port $port (logging to $log)..."
    nohup llama-server \
        --model "$model" \
        --alias "$name" \
        --host 0.0.0.0 \
        --port "$port" \
        -ngl 99 \
        --ctx-size 8192 \
        --cache-ram 0 \
        $extra_args \
        > "$log" 2>&1 &

    sleep 2
    if lsof -i ":$port" 2>/dev/null | grep -q LISTEN; then
        echo "✓ $name running on port $port"
    else
        echo "✗ $name failed to start. Check $log"
        return 1
    fi
}

stop_server() {
    local port="$1"
    local pid=$(lsof -ti ":$port" 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Stopping server on port $port (pid $pid)..."
        kill "$pid" && sleep 2
    fi
}

case "${1:-start}" in
    start)
        # Main model: Qwen3-VL-30B, thinking ON by default
        start_server "qwen3-vl-30b-a3b" \
            "$MAIN_MODEL" 38000 \
            "--mmproj $MAIN_MMPROJ --chat-template-kwargs '{\"enable_thinking\":true}'"

        # Helper: Qwen-AgentWorld, thinking OFF (it's a simulator)
        start_server "qwen-agentworld-35b-a3b" \
            "$AGENT_WORLD_MODEL" 38001 \
            "--ctx-size 16384 --chat-template-kwargs '{\"enable_thinking\":false}'"

        echo ""
        echo "Both servers started. Verify with:"
        echo "  curl http://localhost:38000/v1/models"
        echo "  curl http://localhost:38001/v1/models"
        ;;

    stop)
        stop_server 38000
        stop_server 38001
        ;;

    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
