#!/usr/bin/env python3
"""
Snoopy Model Builder using Goxel Daemon JSON-RPC API
Creates a 3D voxel model of Snoopy with proper colors
"""

import socket
import json
import time
import sys
import os

SOCKET_PATH = "/Users/jimmy/jimmy_side_projects/goxel/snoopy_test/goxel.sock"

class GoxelClient:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        self.request_id = 1

    def connect(self):
        """Connect to the goxel daemon"""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        print(f"Connected to goxel daemon at {self.socket_path}")

    def disconnect(self):
        """Disconnect from the daemon"""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Disconnected from goxel daemon")

    def send_request(self, method, params=None):
        """Send a JSON-RPC request to the daemon"""
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
        
        print(f"Sending: {method}", end="")
        self.sock.send(message.encode())
        
        # Improved response handling with buffer
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
            print(f" - Error: Empty response")
            return None
            
        try:
            parsed_response = json.loads(response)
        except json.JSONDecodeError as e:
            print(f" - Error parsing JSON: {e}")
            print(f" - Raw response: {response}")
            return None
        
        if "error" in parsed_response:
            print(f" - Error: {parsed_response['error']}")
            return None
        else:
            print(" - Success")
            return parsed_response.get("result")

def build_snoopy_model(client):
    """Build a complete Snoopy model"""
    
    print("\n=== Creating Snoopy Project ===")
    # Create a new project for Snoopy
    client.send_request("goxel.create_project", ["Snoopy", 32, 32, 32])
    
    print("\n=== Building Snoopy Body (White) ===")
    # Snoopy's body - white color (255, 255, 255, 255)
    white = [255, 255, 255, 255]
    black = [0, 0, 0, 255]
    
    # Main body - simplified rectangular shape
    voxel_count = 0
    for x in range(12, 20):  # 8 voxels wide
        for y in range(12, 18):  # 6 voxels deep  
            for z in range(8, 14):   # 6 voxels tall
                client.send_request("goxel.add_voxel", [x, y, z] + white)
                voxel_count += 1
    
    print(f"Added {voxel_count} body voxels")
    
    print("\n=== Building Snoopy Head (White) ===")
    # Snoopy's head - simplified oval
    voxel_count = 0
    for x in range(13, 19):  # Head width
        for y in range(11, 17):  # Head depth
            for z in range(14, 20):  # Head height
                # Simple oval check
                dx = (x - 16) / 3    # Center head
                dy = (y - 14) / 3    # Center head  
                dz = (z - 17) / 3    # Center head
                
                if dx*dx + dy*dy + dz*dz <= 1:
                    client.send_request("goxel.add_voxel", [x, y, z] + white)
                    voxel_count += 1
    
    print(f"Added {voxel_count} head voxels")
    
    print("\n=== Building Snoopy Ears (Black) ===")
    # Left ear - simplified
    voxel_count = 0
    for x in range(13, 16):
        for y in range(12, 15):
            for z in range(17, 22):
                client.send_request("goxel.add_voxel", [x, y, z] + black)
                voxel_count += 1
    
    # Right ear - simplified  
    for x in range(17, 20):
        for y in range(12, 15):
            for z in range(17, 22):
                client.send_request("goxel.add_voxel", [x, y, z] + black)
                voxel_count += 1
    
    print(f"Added {voxel_count} ear voxels")
    
    print("\n=== Building Snoopy Features ===")
    # Nose - small black area
    client.send_request("goxel.add_voxel", [16, 10, 17] + black)
    client.send_request("goxel.add_voxel", [16, 9, 17] + black)
    
    # Eyes - small black dots
    client.send_request("goxel.add_voxel", [14, 12, 18] + black)
    client.send_request("goxel.add_voxel", [18, 12, 18] + black)
    
    print("Added nose and eyes")
    
    print("\n=== Building Snoopy Legs (White) ===")
    # Simple leg pillars
    voxel_count = 0
    # Front left leg
    for z in range(5, 9):
        client.send_request("goxel.add_voxel", [13, 15, z] + white)
        voxel_count += 1
    
    # Front right leg
    for z in range(5, 9):
        client.send_request("goxel.add_voxel", [18, 15, z] + white)
        voxel_count += 1
    
    # Back left leg
    for z in range(5, 9):
        client.send_request("goxel.add_voxel", [13, 13, z] + white)
        voxel_count += 1
    
    # Back right leg
    for z in range(5, 9):
        client.send_request("goxel.add_voxel", [18, 13, z] + white)
        voxel_count += 1
    
    print(f"Added {voxel_count} leg voxels")
    
    print("\n=== Building Snoopy Tail (White) ===")
    # Simple curved tail
    voxel_count = 0
    for x in range(20, 24):
        for y in range(13, 16):
            for z in range(10, 13):
                client.send_request("goxel.add_voxel", [x, y, z] + white)
                voxel_count += 1
    
    print(f"Added {voxel_count} tail voxels")
    print("\n=== Snoopy Model Complete! ===")

def main():
    if not os.path.exists(SOCKET_PATH):
        print(f"Error: Socket {SOCKET_PATH} does not exist. Is goxel-daemon running?")
        sys.exit(1)
    
    client = GoxelClient(SOCKET_PATH)
    
    try:
        print("Building Snoopy 3D Model...")
        client.connect()
        
        # Build the complete Snoopy model
        build_snoopy_model(client)
        
        # Save the project
        print("\n=== Saving Project ===")
        client.send_request("goxel.save_project", ["./snoopy_test/snoopy.gox"])
        
        # Render the scene with file-path mode (new in v0.16.1)
        print("\n=== Rendering Scene ===")
        render_result = client.send_request("goxel.render_scene", {
            "width": 800, 
            "height": 600, 
            "options": {"return_mode": "file_path"},
            "output_path": "./snoopy_test/snoopy_render.png"
        })
        
        if render_result:
            print(f"Rendered image saved to: {render_result.get('file_path', 'unknown')}")
        
        print("\n=== Snoopy Model Creation Complete! ===")
        print("Files created:")
        print("- snoopy.gox (3D model)")
        print("- snoopy_render.png (rendered image)")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()