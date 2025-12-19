#!/usr/bin/env python3
"""
Image Generation Monitor for ComfyUI
Shows progress bar, timing, and prompt for each image generated
"""

import urllib.request
import json
import time
import sys
import subprocess
import os
import uuid

PROJECT_DIR = "/Users/matthewmacosko/Desktop/Divine Tribe Email Assistant"
SERVER = "127.0.0.1:8188"

def is_comfyui_running():
    """Check if ComfyUI server is responding"""
    try:
        urllib.request.urlopen("http://127.0.0.1:8188/", timeout=5)
        return True
    except:
        return False

def restart_comfyui():
    """Restart ComfyUI in background"""
    comfyui_dir = os.path.join(PROJECT_DIR, "ComfyUI")
    subprocess.Popen(
        [os.path.join(comfyui_dir, "venv/bin/python3"), "main.py"],
        cwd=comfyui_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def get_queue():
    """Get current ComfyUI queue status"""
    try:
        req = urllib.request.urlopen(f"http://{SERVER}/queue", timeout=5)
        return json.loads(req.read())
    except:
        return None

def warmup_models():
    """Generate a small test image to pre-load FLUX models"""
    print("Loading FLUX models (this takes ~60 seconds)...", flush=True)

    # Small 512x512 image with minimal steps for faster warmup
    workflow = {
        "3": {
            "inputs": {"text": "test", "clip": ["11", 0]},
            "class_type": "CLIPTextEncode"
        },
        "10": {
            "inputs": {"unet_name": "flux1-schnell.safetensors", "weight_dtype": "default"},
            "class_type": "UNETLoader"
        },
        "11": {
            "inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp16.safetensors", "type": "flux"},
            "class_type": "DualCLIPLoader"
        },
        "12": {
            "inputs": {"vae_name": "ae.safetensors"},
            "class_type": "VAELoader"
        },
        "13": {
            "inputs": {
                "noise": ["25", 0], "guider": ["22", 0],
                "sampler": ["16", 0], "sigmas": ["17", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "SamplerCustomAdvanced"
        },
        "22": {
            "inputs": {"conditioning": ["3", 0], "model": ["10", 0]},
            "class_type": "BasicGuider"
        },
        "25": {
            "inputs": {"noise_seed": 12345},
            "class_type": "RandomNoise"
        },
        "16": {
            "inputs": {"sampler_name": "euler"},
            "class_type": "KSamplerSelect"
        },
        "17": {
            "inputs": {"scheduler": "simple", "steps": 2, "denoise": 1.0, "model": ["10", 0]},
            "class_type": "BasicScheduler"
        },
        "5": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptySD3LatentImage"
        },
        "8": {
            "inputs": {"samples": ["13", 0], "vae": ["12", 0]},
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {"filename_prefix": f"warmup_{uuid.uuid4().hex[:8]}", "images": ["8", 0]},
            "class_type": "SaveImage"
        }
    }

    try:
        # Submit warmup prompt
        prompt_data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"http://{SERVER}/api/prompt",
            data=prompt_data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read())
        prompt_id = result.get('prompt_id')

        if not prompt_id:
            print("   Warmup failed - no prompt_id", flush=True)
            return False

        # Wait for completion with progress
        start_time = time.time()
        while time.time() - start_time < 120:
            elapsed = time.time() - start_time
            # Animated progress
            dots = "." * (int(elapsed) % 4)
            print(f"\r   [{elapsed:5.1f}s] Loading{dots:<4}", end="", flush=True)

            queue = get_queue()
            if queue:
                running = queue.get('queue_running', [])
                pending = queue.get('queue_pending', [])
                if not running and not pending:
                    # Check if it completed
                    try:
                        hist_req = urllib.request.urlopen(f"http://{SERVER}/history/{prompt_id}", timeout=5)
                        history = json.loads(hist_req.read())
                        if prompt_id in history:
                            elapsed = time.time() - start_time
                            print(f"\r   Models loaded in {elapsed:.1f}s       ", flush=True)
                            return True
                    except:
                        pass
            time.sleep(0.5)

        print("\r   Warmup timeout                    ", flush=True)
        return False

    except Exception as e:
        print(f"\r   Warmup error: {e}                 ", flush=True)
        return False

def get_history(prompt_id):
    """Get history for a specific prompt"""
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=5)
        return json.loads(req.read())
    except:
        return {}

def extract_prompt_text(queue_item):
    """Extract the text prompt from a queue item"""
    try:
        # queue_item is [index, prompt_id, prompt_data, ...]
        prompt_data = queue_item[2]
        # Look for CLIPTextEncode node (usually node "3")
        for node_id, node in prompt_data.items():
            if node.get('class_type') == 'CLIPTextEncode':
                inputs = node.get('inputs', {})
                text = inputs.get('text', '')
                if text:
                    return text[:60] + "..." if len(text) > 60 else text
    except:
        pass
    return "Unknown prompt"

def progress_bar(elapsed, width=30):
    """Create a simple progress bar based on elapsed time"""
    # Estimate ~15-30 seconds for generation, show indeterminate progress
    cycle = int(elapsed * 2) % width
    bar = "░" * width
    bar = bar[:cycle] + "█" + bar[cycle+1:]
    return bar

def monitor(skip_warmup=False):
    """Main monitoring loop"""
    session_total = 0
    last_prompt_id = None
    start_time = None
    current_prompt = None
    last_health_check = time.time()
    comfyui_online = True

    # Pre-load models at startup
    if not skip_warmup:
        warmup_models()

    print("[Monitor] Ready - watching for image generations...", flush=True)

    while True:
        try:
            # Health check every 60 seconds
            if time.time() - last_health_check > 60:
                last_health_check = time.time()
                if not is_comfyui_running():
                    if comfyui_online:
                        print(f"\n[{time.strftime('%H:%M:%S')}] ComfyUI: OFFLINE - Restarting...", flush=True)
                        comfyui_online = False
                        restart_comfyui()
                elif not comfyui_online:
                    print(f"[{time.strftime('%H:%M:%S')}] ComfyUI: Back online", flush=True)
                    comfyui_online = True

            queue = get_queue()
            if not queue:
                time.sleep(1)
                continue

            running = queue.get('queue_running', [])

            if running:
                # Job is running
                job = running[0]
                prompt_id = job[1]

                if prompt_id != last_prompt_id:
                    # New job started
                    last_prompt_id = prompt_id
                    start_time = time.time()
                    current_prompt = extract_prompt_text(job)
                    print(f"\n[{time.strftime('%H:%M:%S')}] Creating: \"{current_prompt}\"", flush=True)

                # Show progress
                elapsed = time.time() - start_time
                bar = progress_bar(elapsed)
                print(f"\r   [{bar}] {elapsed:.1f}s ", end="", flush=True)

            elif last_prompt_id and start_time:
                # Job just finished
                elapsed = time.time() - start_time
                session_total += 1
                print(f"\r   [{'█' * 30}] Done!      ", flush=True)
                print(f"   Completed in {elapsed:.1f}s (Session total: {session_total})", flush=True)

                last_prompt_id = None
                start_time = None
                current_prompt = None

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[Monitor] Stopped", flush=True)
            break
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    monitor()
