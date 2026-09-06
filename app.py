import os
import sys
import time
import queue
import threading
import subprocess
from flask import Flask, send_from_directory, Response, jsonify

app = Flask(__name__, static_folder='.', static_url_path='')

# Global variables for tracking pipeline state
pipeline_process = None
log_queue = queue.Queue()
pipeline_running = False

PIPELINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily-instagram-posts-pipeline")

def run_pipeline_thread():
    global pipeline_process, pipeline_running
    pipeline_running = True
    
    log_queue.put("[System] Starting Pipeline Subprocess...\n")
    try:
        # Run the instagram pipeline, ensuring python is used and unbuffered
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        
        pipeline_process = subprocess.Popen(
            [sys.executable, "run_instagram_pipeline.py", "--youtube"],
            cwd=PIPELINE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        # Read output line by line
        for line in iter(pipeline_process.stdout.readline, ''):
            if line:
                log_queue.put(line)
        
        pipeline_process.wait()
        log_queue.put(f"[System] Pipeline completed with return code {pipeline_process.returncode}\n")
    except Exception as e:
        log_queue.put(f"[Error] Failed to run pipeline: {e}\n")
    finally:
        pipeline_running = False


@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')


@app.route('/run-pipeline', methods=['POST'])
def start_pipeline():
    global pipeline_running
    if pipeline_running:
        return jsonify({"status": "error", "message": "Pipeline is already running."}), 400
    
    # Start the pipeline in a background thread
    thread = threading.Thread(target=run_pipeline_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "message": "Pipeline started."})


@app.route('/stream-logs')
def stream_logs():
    def event_stream():
        # Send an initial connection success message
        yield "data: [System] Connected to log stream.\n\n"
        
        while True:
            try:
                # Block for a short time to avoid tight loops
                line = log_queue.get(timeout=1.0)
                # Clean line for SSE format
                clean_line = line.replace('\n', '').replace('\r', '')
                yield f"data: {clean_line}\n\n"
            except queue.Empty:
                # Send a ping/keep-alive if no logs
                yield ": keepalive\n\n"
                
                # If pipeline finished and queue is empty, we can stop the stream (optional)
                # For this dashboard, we might want to keep the connection open for next run
                pass
            except GeneratorExit:
                break

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    print("Starting AI Office Control Server on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
