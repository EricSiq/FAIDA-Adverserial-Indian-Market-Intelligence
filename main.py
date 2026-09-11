"""
FAIDA: Financial Adversarial Indian Data Agents
Module: main
Description:
    Primary Desktop Application Entry Point.
    
    Architectural Model:
        - Asynchronous Backend Thread: Spawns the local FastAPI server in a background
          daemon thread powered by Uvicorn.
        - Zero-Flash Active Polling: Actively polls the local healthcheck endpoint
          with low-latency retries rather than relying on arbitrary sleep durations.
        - PyWebView Native Desktop Shell: Embeds a hardware-accelerated desktop window
          with dark navy initial background (#0a0e17) to eliminate white launch flashes.
        - Multi-Modal Runtime Flags:
            --cli     : Direct terminal REPL for headless testing or automated shell scripts.
            --browser : Headless backend server launching the standard system browser.
            Default   : Native desktop GUI window.
"""

import sys
import threading
import time
import webbrowser
import urllib.request
import uvicorn

from backend.config import settings

def run_fastapi():
    """Starts the Uvicorn ASGI server hosting the FAIDA FastAPI backend."""
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="warning",
        access_log=False
    )

def wait_for_server(url: str, timeout_sec: float = 6.0) -> bool:
    """Polls server readiness endpoint with low-latency retries."""
    start_time = time.time()
    while (time.time() - start_time) < timeout_sec:
        try:
            with urllib.request.urlopen(f"{url}/api/config", timeout=0.3) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.05)
    return False

def main():
    url = f"http://{settings.HOST}:{settings.PORT}"
    print(f"[*] Starting FAIDA (Financial Adversarial Indian Data Agents)...")
    print(f"[*] Backend server URL: {url}")

    # Start FastAPI server in background thread
    server_thread = threading.Thread(target=run_fastapi, daemon=True)
    server_thread.start()

    # Active health check instead of blind sleep
    if not wait_for_server(url):
        print(f"[!] Server readiness check timed out. Proceeding to launch...")

    # CLI mode check
    if "--cli" in sys.argv:
        from backend.agents.orchestrator import SwarmOrchestrator
        orch = SwarmOrchestrator()
        print("\n[FAIDA CLI Mode Ready. Type an investment thesis or 'exit']")
        while True:
            try:
                query = input("\nFAIDA> ").strip()
                if query.lower() in ("exit", "quit", "q"):
                    break
                if not query:
                    continue
                print(f"[*] Ingesting data and red-teaming...")
                res = orch.process_investment_query(query, tone_level=3)
                print(f"\n--- VERDICT: {res['pre_mortem']['headline_verdict']} ---")
                print(f"Friction Score: {res['pre_mortem']['friction_score']}/100")
                print(f"\nADVERSARIAL COUNTER-ARGUMENTS:\n{res['adversarial_counter_thesis']}")
            except KeyboardInterrupt:
                break
        sys.exit(0)

    # Browser mode check
    if "--browser" in sys.argv:
        print(f"[*] Opening FAIDA in browser at {url}...")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

    # Native Desktop Window via PyWebView (Zero-Flash dark navy background, text selectable)
    try:
        import webview
        print(f"[*] Launching native desktop window via PyWebView...")
        window = webview.create_window(
            title="FAIDA - Financial Adversarial Indian Data Agents",
            url=url,
            width=1320,
            height=880,
            min_size=(900, 600),
            background_color="#0a0e17",
            text_select=True,
            zoomable=False
        )
        webview.start()
    except Exception as err:
        print(f"[!] PyWebView window launch encountered an issue: {err}")
        print(f"[*] Falling back to default system web browser at {url}...")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()
