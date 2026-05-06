import math
import time
from fastapi import FastAPI, BackgroundTasks

app = FastAPI(title="CACOP Victim Service")

def cpu_intensive_task(duration_seconds: int):
    """Simulates a poorly optimized process or a retry storm."""
    end_time = time.time() + duration_seconds
    # Crunch numbers to max out the CPU thread
    while time.time() < end_time:
        math.factorial(10000)

@app.get("/health")
def health_check():
    """Standard endpoint for K8s liveness probes."""
    return {"status": "healthy", "version": "2"}

@app.get("/api/normal")
def normal_request():
    """Simulates a standard, low-cost API call."""
    return {"message": "Success", "cost_profile": "low"}

@app.post("/api/stress")
def stress_cpu(background_tasks: BackgroundTasks, duration: int = 10):
    """Intentionally spikes CPU to simulate a system fault or traffic surge."""
    background_tasks.add_task(cpu_intensive_task, duration)
    return {"message": f"CPU stress test started for {duration} seconds. Watch the metrics!"}