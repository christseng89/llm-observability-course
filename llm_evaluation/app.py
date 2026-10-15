import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT_DIR))

from src.pipeline import run_ingestion

if __name__ == "__main__":
    run_ingestion()

    streamlit_app = ROOT_DIR / "src" / "app.py"

    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(streamlit_app)]
    )

    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\nStopping Streamlit...")
        streamlit_process.terminate()

        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
            streamlit_process.wait()

        raise SystemExit(0)
