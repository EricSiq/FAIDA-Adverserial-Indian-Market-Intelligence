import sys
import threading
import time
import webbrowser
import uvicorn

from backend.config import settings

def run_fastapi():
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="warning",
        access_log=False
    )

def main():
    url = f"http://{settings.HOST}:{settings.PORT}"
    print(f"[*] Starting FAIDA (Financial Adversarial Indian Data Agents)...")
    print(f"[*] Backend server URL: {url}")

    # Start FastAPI server in background thread
    server_thread = threading.Thread(target=run_fastapi, daemon=True)
    server_thread.start()
    time.sleep(1.2)  # Allow server to initialize

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

    # Native Desktop Window via PyWebView
    try:
        import webview
        print(f"[*] Launching native desktop window via PyWebView...")
        window = webview.create_window(
            title="FAIDA - Financial Adversarial Indian Data Agents",
            url=url,
            width=1320,
            height=880,
            min_size=(900, 600)
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
