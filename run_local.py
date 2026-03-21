"""
Local runner for Meeting Prep Agent

Runs all services locally without containers.
Requires: pip install fastapi uvicorn pydantic httpx streamlit
"""

import subprocess
import sys
import time
import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 60)
    print("Meeting Prep Agent - Local Development Runner")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print()
    
    # Check LLM
    print("[1/6] Checking LLM availability...")
    print("      Make sure IBM Granite model is running in Podman AI Lab on port 65354")
    print()
    
    processes = []
    
    try:
        # Start CRM Agent
        print("[2/6] Starting CRM Agent on port 8001...")
        crm_env = os.environ.copy()
        crm_env["CRM_DATA_PATH"] = os.path.join(PROJECT_ROOT, "data", "crm", "clients.json")
        p1 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "agent:app", "--host", "127.0.0.1", "--port", "8001"],
            cwd=os.path.join(PROJECT_ROOT, "agents", "crm"),
            env=crm_env
        )
        processes.append(("CRM Agent", p1))
        
        # Start Comms Agent
        print("[3/6] Starting Comms Agent on port 8002...")
        comms_env = os.environ.copy()
        comms_env["COMMS_DATA_PATH"] = os.path.join(PROJECT_ROOT, "data", "slack")
        p2 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "agent:app", "--host", "127.0.0.1", "--port", "8002"],
            cwd=os.path.join(PROJECT_ROOT, "agents", "email"),
            env=comms_env
        )
        processes.append(("Comms Agent", p2))
        
        # Start Docs Agent
        print("[4/6] Starting Docs Agent on port 8003...")
        docs_env = os.environ.copy()
        docs_env["DOCS_DATA_PATH"] = os.path.join(PROJECT_ROOT, "data", "documents")
        p3 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "agent:app", "--host", "127.0.0.1", "--port", "8003"],
            cwd=os.path.join(PROJECT_ROOT, "agents", "docs"),
            env=docs_env
        )
        processes.append(("Docs Agent", p3))
        
        # Start Analytics Agent
        print("[5/6] Starting Analytics Agent on port 8004...")
        analytics_env = os.environ.copy()
        analytics_env["ANALYTICS_DATA_PATH"] = os.path.join(PROJECT_ROOT, "data", "analytics")
        p4 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "agent:app", "--host", "127.0.0.1", "--port", "8004"],
            cwd=os.path.join(PROJECT_ROOT, "agents", "analytics"),
            env=analytics_env
        )
        processes.append(("Analytics Agent", p4))
        
        # Wait for agents to start
        print("      Waiting for agents to initialize...")
        time.sleep(3)
        
        # Start Orchestrator
        print("[6/6] Starting Orchestrator on port 8000...")
        orch_env = os.environ.copy()
        orch_env["LLM_URL"] = "http://127.0.0.1:65354"
        orch_env["CRM_AGENT_URL"] = "http://127.0.0.1:8001"
        orch_env["COMMS_AGENT_URL"] = "http://127.0.0.1:8002"
        orch_env["DOCS_AGENT_URL"] = "http://127.0.0.1:8003"
        orch_env["ANALYTICS_AGENT_URL"] = "http://127.0.0.1:8004"
        p5 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=os.path.join(PROJECT_ROOT, "orchestrator"),
            env=orch_env
        )
        processes.append(("Orchestrator", p5))
        
        # Wait for orchestrator
        time.sleep(2)
        
        print()
        print("=" * 60)
        print("All services started!")
        print()
        print("  Orchestrator API: http://127.0.0.1:8000")
        print("  CRM Agent:        http://127.0.0.1:8001")
        print("  Comms Agent:      http://127.0.0.1:8002")
        print("  Docs Agent:       http://127.0.0.1:8003")
        print("  Analytics Agent:  http://127.0.0.1:8004")
        print()
        print("To test the API:")
        print('  curl -X POST http://127.0.0.1:8000/briefing -H "Content-Type: application/json" -d "{\\"client_name\\": \\"Acme Corp\\", \\"meeting_topic\\": \\"Q1 Review\\"}"')
        print()
        print("Or start the UI in a new terminal:")
        print(f'  cd "{os.path.join(PROJECT_ROOT, "ui")}"')
        print("  streamlit run app.py")
        print()
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Wait for processes
        while True:
            for name, p in processes:
                if p.poll() is not None:
                    print(f"\n{name} exited with code {p.returncode}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        for name, p in processes:
            print(f"  Stopping {name}...")
            p.terminate()
        print("All services stopped.")


if __name__ == "__main__":
    main()
