"""
Image Generation Module using FLUX workflow format
With improved tunnel detection and fast-fail for better reliability
"""

import json
import urllib.request
import base64
import time
import glob
import os
import uuid
import sys


def print_progress_bar(current, total, prefix='', suffix='', length=40):
    """Print a progress bar to the terminal"""
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    sys.stdout.write(f'\r{prefix} [{bar}] {int(percent*100)}% {suffix}')
    sys.stdout.flush()


class ImageGenerator:
    def __init__(self):
        self.server_address = "127.0.0.1:8188"
        self.lora_name = "flux-realism-xlabs.safetensors"
        self.lora_strength = 2.0
        self.model_loaded = False

    def warmup_model(self):
        """
        Pre-load the FLUX model into VRAM by generating a tiny test image.
        Call this at startup so first real request doesn't timeout.
        """
        if not self.check_comfyui_running():
            print("⚠️  ComfyUI not running - skipping model warmup")
            return False

        if self.model_loaded:
            print("✅ FLUX model already loaded")
            return True

        print("🔄 Loading FLUX model into VRAM...")

        # Generate a tiny 256x256 test image to load the model
        warmup_workflow = {
            "10": {
                "inputs": {
                    "unet_name": "flux1-schnell.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader"
            },
            "11": {
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp16.safetensors",
                    "type": "flux"
                },
                "class_type": "DualCLIPLoader"
            },
            "12": {
                "inputs": {"vae_name": "ae.safetensors"},
                "class_type": "VAELoader"
            },
            "3": {
                "inputs": {
                    "text": "test",
                    "clip": ["11", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {
                "inputs": {"width": 256, "height": 256, "batch_size": 1},
                "class_type": "EmptySD3LatentImage"
            },
            "22": {
                "inputs": {
                    "conditioning": ["3", 0],
                    "model": ["10", 0]
                },
                "class_type": "BasicGuider"
            },
            "25": {
                "inputs": {"noise_seed": 1},
                "class_type": "RandomNoise"
            },
            "16": {
                "inputs": {"sampler_name": "euler"},
                "class_type": "KSamplerSelect"
            },
            "17": {
                "inputs": {
                    "scheduler": "simple",
                    "steps": 1,  # Just 1 step for warmup
                    "denoise": 1.0,
                    "model": ["10", 0]
                },
                "class_type": "BasicScheduler"
            },
            "13": {
                "inputs": {
                    "noise": ["25", 0],
                    "guider": ["22", 0],
                    "sampler": ["16", 0],
                    "sigmas": ["17", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "SamplerCustomAdvanced"
            },
            "8": {
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["12", 0]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "warmup_delete",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        try:
            prompt_data = json.dumps({"prompt": warmup_workflow}).encode('utf-8')
            req = urllib.request.Request(
                f"http://{self.server_address}/api/prompt",
                data=prompt_data,
                headers={'Content-Type': 'application/json'}
            )

            response = urllib.request.urlopen(req, timeout=120)  # 2 min timeout for warmup
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id')

            if prompt_id and self._wait_for_warmup(prompt_id, timeout=90):
                self.model_loaded = True
                print("")  # New line after progress bar

                # Clean up warmup image
                output_dir = "/Users/matthewmacosko/Desktop/Divine Tribe Email Assistant/ComfyUI/output"
                warmup_images = glob.glob(f"{output_dir}/warmup_delete*.png")
                for img in warmup_images:
                    try:
                        os.remove(img)
                    except:
                        pass

                return True
            else:
                print("⚠️  Model warmup timed out")
                return False

        except Exception as e:
            print(f"⚠️  Model warmup error: {e}")
            return False

    def check_comfyui_running(self):
        """Check if ComfyUI server is running"""
        try:
            urllib.request.urlopen(f"http://{self.server_address}/", timeout=3)
            return True
        except Exception as e:
            return False

    def wait_for_image(self, prompt_id, timeout=120):
        """
        Wait for ComfyUI to finish generating.
        IMPROVED: Fail fast if tunnel appears to be down (consecutive connection errors)
        """
        start_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 5  # Fail fast after 5 consecutive connection errors

        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(f"http://{self.server_address}/history/{prompt_id}")
                response = urllib.request.urlopen(req, timeout=5)
                history = json.loads(response.read())

                # Reset error counter on successful connection
                consecutive_errors = 0

                if prompt_id in history:
                    if history[prompt_id].get('outputs'):
                        return True

            except urllib.error.URLError as e:
                consecutive_errors += 1
                print(f"Fetch attempt error: {e.reason}")

                # Fast-fail if tunnel appears to be down
                if consecutive_errors >= max_consecutive_errors:
                    print(f"❌ Connection appears to be down ({consecutive_errors} consecutive errors)")
                    return False

            except Exception as e:
                consecutive_errors += 1
                print(f"Fetch error: {e}")

                if consecutive_errors >= max_consecutive_errors:
                    print(f"❌ Too many errors ({consecutive_errors}), giving up")
                    return False

            time.sleep(2)
        return False

    def wait_and_fetch_image(self, prompt_id, timeout=120):
        """
        Wait for ComfyUI to finish generating, then fetch the image via API.
        This works over network tunnels - doesn't require filesystem access.
        """
        start_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 10  # More tolerant for network hiccups

        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(f"http://{self.server_address}/history/{prompt_id}")
                response = urllib.request.urlopen(req, timeout=10)
                history = json.loads(response.read())

                # Reset error counter on successful connection
                consecutive_errors = 0

                if prompt_id in history:
                    outputs = history[prompt_id].get('outputs', {})
                    if outputs:
                        # Find the SaveImage node output (usually node "9")
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                for img_info in node_output['images']:
                                    filename = img_info.get('filename')
                                    subfolder = img_info.get('subfolder', '')
                                    img_type = img_info.get('type', 'output')

                                    if filename:
                                        # Fetch the image via /view endpoint
                                        img_data = self._fetch_image_from_api(filename, subfolder, img_type)
                                        if img_data:
                                            return img_data

                        # If we got outputs but no images, something went wrong
                        print("⚠️ Generation completed but no images found in output")
                        return None

            except urllib.error.URLError as e:
                consecutive_errors += 1
                if consecutive_errors % 3 == 0:  # Log every 3rd error to reduce spam
                    print(f"Fetch attempt error: {e.reason}")

                # More tolerant - only fail after more errors over longer period
                if consecutive_errors >= max_consecutive_errors:
                    elapsed = time.time() - start_time
                    if elapsed > 30:  # Only give up if we've tried for 30+ seconds
                        print(f"❌ Tunnel appears down ({consecutive_errors} errors over {elapsed:.0f}s)")
                        return None

            except Exception as e:
                consecutive_errors += 1
                print(f"Fetch error: {e}")

                if consecutive_errors >= max_consecutive_errors:
                    return None

            time.sleep(2)

        print(f"❌ Timeout after {timeout}s waiting for image")
        return None

    def _fetch_image_from_api(self, filename, subfolder, img_type):
        """Fetch image data from ComfyUI's /view endpoint"""
        try:
            import urllib.parse
            params = urllib.parse.urlencode({
                'filename': filename,
                'subfolder': subfolder,
                'type': img_type
            })
            url = f"http://{self.server_address}/view?{params}"

            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=30)
            img_bytes = response.read()

            if img_bytes and len(img_bytes) > 1000:  # Sanity check - image should be >1KB
                img_base64 = base64.b64encode(img_bytes).decode()
                print(f"✅ Fetched image via API: {filename} ({len(img_bytes)} bytes)")
                return img_base64
            else:
                print(f"⚠️ Image too small or empty: {len(img_bytes) if img_bytes else 0} bytes")
                return None

        except Exception as e:
            print(f"❌ Failed to fetch image {filename}: {e}")
            return None

    def _wait_for_warmup(self, prompt_id, timeout=90):
        """Wait for warmup with progress bar"""
        start_time = time.time()
        check_interval = 1  # Check every second
        consecutive_errors = 0

        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            # Estimate progress (FLUX typically takes 30-60 seconds)
            estimated_total = 45  # Estimate 45 seconds for warmup
            progress = min(elapsed / estimated_total, 0.99)  # Cap at 99% until done

            print_progress_bar(
                progress, 1.0,
                prefix='   FLUX',
                suffix='Loading...',
                length=30
            )

            try:
                req = urllib.request.Request(f"http://{self.server_address}/history/{prompt_id}")
                response = urllib.request.urlopen(req, timeout=5)
                history = json.loads(response.read())
                consecutive_errors = 0

                if prompt_id in history:
                    if history[prompt_id].get('outputs'):
                        # Complete!
                        print_progress_bar(1.0, 1.0, prefix='   FLUX', suffix='Complete!', length=30)
                        return True

            except:
                consecutive_errors += 1
                if consecutive_errors >= 10:
                    return False
                pass
            time.sleep(check_interval)

        return False

    def generate_for_chatbot(self, prompt):
        """
        Generate image using proper FLUX workflow with separate VAE loader.
        IMPROVED: Better error handling and connection detection.
        """

        # Quick connectivity check before we start
        if not self.check_comfyui_running():
            print("❌ ComfyUI not responding")
            return {'has_image': False, 'error': 'Image generator offline - please try again in a moment'}

        # Use unique filename for each generation
        filename_prefix = f"divtribe_{str(uuid.uuid4())[:8]}"

        workflow = {
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]  # Use DualCLIPLoader
                },
                "class_type": "CLIPTextEncode"
            },
            "10": {
                "inputs": {
                    "unet_name": "flux1-schnell.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader"
            },
            "11": {
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp16.safetensors",
                    "type": "flux"
                },
                "class_type": "DualCLIPLoader"
            },
            "12": {
                "inputs": {"vae_name": "ae.safetensors"},
                "class_type": "VAELoader"
            },
            "13": {
                "inputs": {
                    "noise": ["25", 0],
                    "guider": ["22", 0],
                    "sampler": ["16", 0],
                    "sigmas": ["17", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "SamplerCustomAdvanced"
            },
            "22": {
                "inputs": {
                    "conditioning": ["3", 0],
                    "model": ["10", 0]
                },
                "class_type": "BasicGuider"
            },
            "25": {
                "inputs": {"noise_seed": int(time.time())},
                "class_type": "RandomNoise"
            },
            "16": {
                "inputs": {"sampler_name": "euler"},
                "class_type": "KSamplerSelect"
            },
            "17": {
                "inputs": {
                    "scheduler": "simple",
                    "steps": 4,
                    "denoise": 1.0,
                    "model": ["10", 0]
                },
                "class_type": "BasicScheduler"
            },
            "5": {
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                "class_type": "EmptySD3LatentImage"
            },
            "8": {
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["12", 0]  # Use separate VAELoader
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": filename_prefix,
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        try:
            # Submit prompt with timeout
            prompt_data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request(
                f"http://{self.server_address}/api/prompt",
                data=prompt_data,
                headers={'Content-Type': 'application/json'}
            )

            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id')

            if not prompt_id:
                print("❌ No prompt_id received from ComfyUI")
                return {'has_image': False, 'error': 'Failed to submit to image generator'}

            # Wait for generation to complete and fetch image via API
            image_data = self.wait_and_fetch_image(prompt_id)
            if image_data:
                return {'has_image': True, 'image_data': image_data}

            print("❌ Image generation failed or timed out")
            return {'has_image': False, 'error': 'Generation timed out - please try again'}

        except urllib.error.URLError as e:
            print(f"Connection error: {e.reason}")
            return {'has_image': False, 'error': 'Image generator connection lost - please try again'}
        except Exception as e:
            print(f"Generation error: {e}")
            return {'has_image': False, 'error': str(e)}
