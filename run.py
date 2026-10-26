"""
ShopSense - Unified Project Runner
Launches both the FastAPI REST Backend and the Streamlit Dashboard
simultaneously using a single command:

    python run.py
"""

import os
import sys
import time
import signal
import subprocess
import urllib.request

def is_backend_healthy(url="http://127.0.0.1:8000/health") -> bool:
    """Checks if the FastAPI backend is already running and healthy."""
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False

def wait_for_backend(url="http://127.0.0.1:8000/health", timeout=12) -> bool:
    """Waits for the FastAPI backend to respond healthy."""
    print("⏳ Waiting for FastAPI backend to initialize...", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_backend_healthy(url):
            print("✅ FastAPI backend is healthy and responding!", flush=True)
            return True
        time.sleep(0.5)
    print("⚠️ Backend took longer than expected to initialize. Proceeding to launch dashboard...", flush=True)
    return False

def kill_process_tree(pid: int):
    """Cleanly terminates a process and all its child subprocesses."""
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("=" * 65)
    print("🛍️   SHOPSENSE – MULTI-VENDOR MARKETPLACE & ANALYTICS")
    print("=" * 65)

    backend_proc = None

    # Check if backend is already running (e.g. from a separate terminal)
    if is_backend_healthy():
        print("ℹ️  FastAPI backend is already running on http://127.0.0.1:8000")
    else:
        print("🚀 Starting FastAPI backend (http://127.0.0.1:8000)...", flush=True)
        backend_cmd = [
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ]
        backend_proc = subprocess.Popen(backend_cmd)
        wait_for_backend()

    # Launch Streamlit frontend
    dashboard_path = os.path.join(project_dir, "dashboard", "dashboard.py")
    print("✨ Starting Streamlit dashboard (http://localhost:8501)...", flush=True)
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run",
        dashboard_path,
        "--server.port", "8501"
    ]
    frontend_proc = subprocess.Popen(streamlit_cmd)

    print("\n" + "=" * 65)
    print("🎉 Both services are running successfully!")
    print("   👉 Dashboard: http://localhost:8501")
    print("   👉 API Docs:  http://127.0.0.1:8000/docs")
    print("   👉 Health:    http://127.0.0.1:8000/health")
    print("=" * 65)
    print("Press Ctrl+C at any time to shut down both servers.\n", flush=True)

    def shutdown(signum=None, frame=None):
        print("\n🛑 Shutting down ShopSense servers...", flush=True)
        if frontend_proc and frontend_proc.poll() is None:
            kill_process_tree(frontend_proc.pid)
        if backend_proc and backend_proc.poll() is None:
            kill_process_tree(backend_proc.pid)
        print("👋 All ShopSense services stopped cleanly. Goodbye!")
        sys.exit(0)

    # Register signal handlers for Ctrl+C
    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    # Monitor child processes
    try:
        while True:
            time.sleep(1)
            # If frontend is closed by user, exit cleanly
            if frontend_proc.poll() is not None:
                print("ℹ️ Streamlit dashboard closed.")
                shutdown()
            if backend_proc and backend_proc.poll() is not None:
                print("❌ FastAPI backend terminated unexpectedly.")
                shutdown()
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
