#!/usr/bin/env python3
"""
Debug rendering issues with Snoopy model
"""

import socket
import json
import os

SOCKET_PATH = "./snoopy_test/goxel.sock"

class DebugClient:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        self.request_id = 1

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)

    def disconnect(self):
        if self.sock:
            self.sock.close()

    def send_request(self, method, params=None):
        if params is None:
            params = []
        
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        
        self.request_id += 1
        message = json.dumps(request) + "\n"
        
        print(f"\n🔍 Testing: {method}")
        self.sock.send(message.encode())
        
        response_data = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b'\n' in response_data:
                break
        
        response = response_data.decode().strip()
        if not response:
            print("❌ Empty response")
            return None
            
        try:
            parsed_response = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ JSON error: {e}")
            return None
        
        if "error" in parsed_response:
            print(f"❌ API Error: {parsed_response['error']}")
            return None
        else:
            result = parsed_response.get("result")
            print(f"✅ Success: {result}")
            return result

def main():
    print("🔧 DEBUGGING SNOOPY RENDER ISSUE")
    print("=" * 50)
    
    client = DebugClient(SOCKET_PATH)
    client.connect()
    
    try:
        # 1. Check project status
        print("\n📋 Step 1: Check project status")
        status = client.send_request("goxel.get_status")
        
        # 2. Load project
        print("\n📁 Step 2: Load Snoopy project")
        load_result = client.send_request("goxel.load_project", ["./snoopy_test/snoopy.gox"])
        
        # 3. Get project info after loading
        print("\n📊 Step 3: Get project info")
        status_after = client.send_request("goxel.get_status")
        
        # 4. Check voxel count
        print("\n🔍 Step 4: Check some voxel positions")
        test_positions = [
            [16, 16, 16],  # Center should have white voxel
            [14, 12, 18],  # Left eye should be black
            [18, 12, 18],  # Right eye should be black
        ]
        
        for pos in test_positions:
            voxel = client.send_request("goxel.get_voxel", pos)
        
        # 5. Get bounding box
        print("\n📏 Step 5: Get bounding box")
        bbox = client.send_request("goxel.get_bounding_box")
        
        # 6. Try render with different settings
        print("\n🖼️ Step 6: Try render with camera settings")
        render_result = client.send_request("goxel.render_scene", {
            "width": 400, 
            "height": 300,
            "camera": {
                "distance": 50,
                "yaw": 45,
                "pitch": 30
            },
            "options": {"return_mode": "file_path"}
        })
        
        # 7. Try simple render parameters
        print("\n🎨 Step 7: Try simple render")
        simple_render = client.send_request("goxel.render_scene", [
            "./snoopy_test/snoopy_debug.png", 
            800, 
            600
        ])
        
        # 8. Check layers
        print("\n📑 Step 8: List layers")
        layers = client.send_request("goxel.list_layers")
        
        # 9. Try to get layer voxels
        print("\n🎯 Step 9: Get layer voxels")
        layer_voxels = client.send_request("goxel.get_layer_voxels", [0])  # Default layer
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    finally:
        client.disconnect()

    print("\n📋 DIAGNOSIS COMPLETE")
    print("Check the debug output above to identify the rendering issue.")

if __name__ == "__main__":
    main()