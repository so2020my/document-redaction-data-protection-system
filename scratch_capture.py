import subprocess
import time
import json
import base64
import urllib.request
import asyncio
import websockets
import os

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE_DIR = r"C:\Users\USER\AppData\Local\Temp\edge_cdp_profile_final3"

async def capture_all():
    edge_proc = subprocess.Popen([
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        f"--user-data-dir={PROFILE_DIR}",
        "--window-size=1440,1000",
        "about:blank"
    ])
    
    time.sleep(2)
    try:
        req = urllib.request.urlopen("http://localhost:9222/json")
        targets = json.loads(req.read().decode())
        page_target = next((t for t in targets if t.get("type") == "page"), targets[0])
        ws_url = page_target["webSocketDebuggerUrl"]
        print(f"Connecting to ws: {ws_url}")
        
        async with websockets.connect(ws_url, max_size=30*1024*1024) as ws:
            msg_id = 100
            
            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                curr_id = msg_id
                payload = {"id": curr_id, "method": method}
                if params:
                    payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    resp = await ws.recv()
                    data = json.loads(resp)
                    if data.get("id") == curr_id:
                        return data

            pages = [
                ("http://localhost:8501/?page=scan", "page_after_fix_1_scan_initial.png"),
                ("http://localhost:8501/?demo=1&page=scan", "page_after_fix_2_scan_file_selected.png"),
                ("http://localhost:8501/?demo=1&page=masking", "page_after_fix_3_masking.png"),
                ("http://localhost:8501/?demo=1&page=report", "page_after_fix_4_report.png"),
            ]
            
            for url, out_file in pages:
                print(f"Navigating to {url}...")
                await send_cmd("Page.navigate", {"url": "about:blank"})
                await asyncio.sleep(0.5)
                await send_cmd("Page.navigate", {"url": url})
                
                # Wait for page readiness
                for i in range(25):
                    await asyncio.sleep(0.8)
                    check_js = """
                    (() => {
                        const hasMain = document.querySelector('[data-testid="stMainBlockContainer"]') !== null;
                        const isRunning = document.querySelector('[data-testid="stStatusWidget"]') !== null 
                                          || document.querySelector('button[aria-label="Stop"]') !== null;
                        const skeletons = document.querySelectorAll('[data-testid="stSkeleton"]').length;
                        return hasMain && !isRunning && skeletons === 0;
                    })()
                    """
                    res = await send_cmd("Runtime.evaluate", {"expression": check_js})
                    is_ready = res.get("result", {}).get("result", {}).get("value", False)
                    if is_ready and i >= 2:
                        print(f"Page ready after ~{(i+1)*0.8:.1f}s")
                        break
                
                await asyncio.sleep(1.2)
                
                # Capture screenshot
                resp = await send_cmd("Page.captureScreenshot", {"format": "png"})
                if "result" in resp and "data" in resp["result"]:
                    img_bytes = base64.b64decode(resp["result"]["data"])
                    with open(out_file, "wb") as f:
                        f.write(img_bytes)
                    print(f"Successfully saved {out_file} ({len(img_bytes)} bytes)")
                else:
                    print(f"Error capturing {out_file}: {resp}")
    finally:
        edge_proc.terminate()
        edge_proc.wait()

if __name__ == "__main__":
    asyncio.run(capture_all())
