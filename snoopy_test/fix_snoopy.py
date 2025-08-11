#!/usr/bin/env python3
"""
Fixed Snoopy Model - Create a properly positioned and visible model
"""

import socket
import json
import os

SOCKET_PATH = "./snoopy_test/goxel.sock"

class FixedGoxelClient:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        self.request_id = 1

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        print("Connected to goxel daemon")

    def disconnect(self):
        if self.sock:
            self.sock.close()
            print("Disconnected")

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
        if response:
            try:
                parsed_response = json.loads(response)
                if "error" in parsed_response:
                    print(f"Error in {method}: {parsed_response['error']}")
                    return None
                return parsed_response.get("result")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None
        return None

def build_centered_snoopy(client):
    """Build a Snoopy model centered at origin (0,0,0) for proper visibility"""
    
    print("Creating new Snoopy project...")
    client.send_request("goxel.create_project", ["CenteredSnoopy", 64, 64, 64])
    
    # Colors
    white = [255, 255, 255, 255]
    black = [0, 0, 0, 255]
    
    print("Building body (centered around origin)...")
    voxel_count = 0
    
    # Body - centered around origin
    for x in range(-4, 5):     # 9 voxels wide
        for y in range(-3, 4):  # 7 voxels deep  
            for z in range(-2, 3):  # 5 voxels tall
                client.send_request("goxel.add_voxel", [x, y, z] + white)
                voxel_count += 1
    
    print(f"Added {voxel_count} body voxels")
    
    # Head - above body
    print("Building head...")
    head_count = 0
    for x in range(-3, 4):      # Head width
        for y in range(-2, 3):   # Head depth
            for z in range(3, 8):    # Head height (above body)
                # Oval shape
                if abs(x) <= 3 and abs(y) <= 2:
                    client.send_request("goxel.add_voxel", [x, y, z] + white)
                    head_count += 1
    
    print(f"Added {head_count} head voxels")
    
    # Ears - black
    print("Building ears...")
    ear_count = 0
    
    # Left ear
    for x in range(-4, -2):
        for y in range(-1, 2):
            for z in range(5, 9):
                client.send_request("goxel.add_voxel", [x, y, z] + black)
                ear_count += 1
    
    # Right ear  
    for x in range(3, 5):
        for y in range(-1, 2):
            for z in range(5, 9):
                client.send_request("goxel.add_voxel", [x, y, z] + black)
                ear_count += 1
    
    print(f"Added {ear_count} ear voxels")
    
    # Face features
    print("Adding face features...")
    
    # Nose
    client.send_request("goxel.add_voxel", [0, -3, 5] + black)
    client.send_request("goxel.add_voxel", [0, -4, 5] + black)
    
    # Eyes
    client.send_request("goxel.add_voxel", [-2, -2, 6] + black)
    client.send_request("goxel.add_voxel", [2, -2, 6] + black)
    
    # Legs
    print("Building legs...")
    leg_count = 0
    
    # Four legs
    positions = [[-2, -2], [2, -2], [-2, 2], [2, 2]]
    for x, y in positions:
        for z in range(-6, -1):  # Below body
            client.send_request("goxel.add_voxel", [x, y, z] + white)
            leg_count += 1
    
    print(f"Added {leg_count} leg voxels")
    
    # Tail
    print("Building tail...")
    tail_count = 0
    for x in range(4, 8):
        for y in range(-1, 2):
            for z in range(-1, 2):
                client.send_request("goxel.add_voxel", [x, y, z] + white)
                tail_count += 1
    
    print(f"Added {tail_count} tail voxels")
    
    total_voxels = voxel_count + head_count + ear_count + 4 + leg_count + tail_count  # +4 for face features
    print(f"\n✅ Total voxels: {total_voxels}")
    
    return total_voxels

def main():
    print("🔧 FIXING SNOOPY RENDERING ISSUE")
    print("Creating a properly centered and visible model...")
    
    client = FixedGoxelClient(SOCKET_PATH)
    
    try:
        client.connect()
        
        # Build new centered model
        total_voxels = build_centered_snoopy(client)
        
        # Save project
        print("\nSaving project...")
        client.send_request("goxel.save_project", ["./snoopy_test/snoopy_fixed.gox"])
        
        # Render with proper camera settings
        print("Rendering with proper camera...")
        render_result = client.send_request("goxel.render_scene", {
            "width": 800, 
            "height": 600,
            "camera": {
                "distance": 25,    # Closer to model
                "yaw": 45,         # Angle view
                "pitch": -20       # Look down slightly
            },
            "output_path": "./snoopy_test/snoopy_fixed.png"
        })
        
        if render_result:
            print(f"✅ Render successful: {render_result}")
        
        # Also try direct PNG method
        print("Trying direct PNG render...")
        direct_result = client.send_request("goxel.render_scene", [
            "./snoopy_test/snoopy_fixed_direct.png", 
            600, 
            450
        ])
        
        if direct_result:
            print(f"✅ Direct render successful: {direct_result}")
        
        print(f"\n🎉 Fixed Snoopy model complete!")
        print(f"📊 Total voxels: {total_voxels}")
        print(f"📁 Files created:")
        print(f"   - snoopy_fixed.gox")
        print(f"   - snoopy_fixed.png")  
        print(f"   - snoopy_fixed_direct.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()