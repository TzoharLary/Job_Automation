#!/usr/bin/env bash
# macOS double-click launcher — restart server if running, then open UI
cd "$(dirname "$0")" || exit 1

# get any PIDs listening on TCP port 8000
# lsof -ti tcp:8000 returns only PIDs (or empty)
PIDS=$(lsof -ti tcp:8000 2>/dev/null || true)
if [ -n "$PIDS" ]; then
	echo "Server detected on port 8000 (PID(s): $PIDS). Stopping..."
	kill $PIDS 2>/dev/null || true
	# give processes a moment to exit
	sleep 1
	for i in {1..10}; do
		STILL=$(lsof -ti tcp:8000 2>/dev/null || true)
		[ -z "$STILL" ] && break
		sleep 1
	done
	STILL=$(lsof -ti tcp:8000 2>/dev/null || true)
	if [ -n "$STILL" ]; then
		echo "Force-killing remaining PID(s): $STILL"
		kill -9 $STILL 2>/dev/null || true
		sleep 1
	fi
else
	echo "No server detected on port 8000. Starting a new server..."
fi

# Start the app runner in background so we can open the browser after it boots
if [ -x "./scripts/run_app.sh" ]; then
	"./scripts/run_app.sh" >/tmp/job_automation_server.log 2>&1 &
	RUN_PID=$!
	echo "Launched ./scripts/run_app.sh (PID $RUN_PID) — logging to /tmp/job_automation_server.log"
else
	echo "./scripts/run_app.sh not executable or missing — attempting with bash"
	bash ./scripts/run_app.sh >/tmp/job_automation_server.log 2>&1 &
	RUN_PID=$!
	echo "Launched run_app.sh via bash (PID $RUN_PID) — logging to /tmp/job_automation_server.log"
fi

# Wait for the server to start listening on port 8000 (timeout 30s)
TIMEOUT=30
for i in $(seq 1 $TIMEOUT); do
	if lsof -ti tcp:8000 >/dev/null 2>&1; then
		echo "Server is listening on port 8000"
		break
	fi
	sleep 1
done

# open the UI in the default browser
open "http://localhost:8000/ui" >/dev/null 2>&1 || true

exit 0
