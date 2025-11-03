"""
Image Generation Module using FLUX workflow format
"""

import json
import urllib.request
import base64
import time
import glob
import os
import uuid

class ImageGenerator:
    def __init__(self):
        self.server_address = "127.0.0.1:8188"
        self.lora_name = "flux-realism-xlabs.safetensors"
        self.lora_strength = 2.0
        
    def check_comfyui_running(self):
        """Check if ComfyUI server is running"""
        try:
            urllib.request.urlopen(f"http://{self.server_address}/", timeout=2)
            return True
        except:
            return False
    
    def wait_for_image(self, prompt_id, timeout=90):
        """Wait for ComfyUI to finish generating"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(f"http://{self.server_address}/history/{prompt_id}")
                response = urllib.request.urlopen(req)
                history = json.loads(response.read())
                
                if prompt_id in history:
                    if history[prompt_id].get('outputs'):
                        return True
                    
            except:
                pass
            time.sleep(2)
        return False
    
    def generate_for_chatbot(self, prompt):
        """Generate image using the same workflow as simple_flux_app"""
        
        # Use unique filename for each generation
        filename_prefix = f"divtribe_{str(uuid.uuid4())[:8]}"
        
        workflow = {
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]
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
                    "model": ["30", 0]  # Use LoRA model
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
                    "model": ["30", 0]  # Use LoRA model
                },
                "class_type": "BasicScheduler"
            },
            "5": {
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                "class_type": "EmptySD3LatentImage"
            },
            "30": {
                "inputs": {
                    "lora_name": self.lora_name,
                    "strength_model": self.lora_strength,
                    "model": ["10", 0]
                },
                "class_type": "LoraLoaderModelOnly"
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
                    "filename_prefix": filename_prefix,
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        try:
            # Submit prompt
            prompt_data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request(
                f"http://{self.server_address}/api/prompt",
                data=prompt_data,
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id')
            
            # Wait for generation to complete
            if prompt_id and self.wait_for_image(prompt_id):
                # Look for the generated image
                output_dir = "/Users/matthewmacosko/Desktop/ComfyUI-FLUX-Project/ComfyUI/output"
                pattern = f"{output_dir}/{filename_prefix}*.png"
                
                # Give it a moment for file to be written
                time.sleep(2)
                
                images = glob.glob(pattern)
                if images:
                    with open(images[0], 'rb') as f:
                        img_base64 = base64.b64encode(f.read()).decode()
                    
                    # Clean up - delete the image after encoding
                    os.remove(images[0])
                    
                    return {'has_image': True, 'image_data': img_base64}
                
        except Exception as e:
            print(f"Generation error: {e}")
            
        return {'has_image': False}
