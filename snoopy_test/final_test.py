#!/usr/bin/env python3
"""
Final test with bright colors and proper camera settings
"""

import socket
import json

SOCKET_PATH = "./snoopy_test/goxel.sock"

class FinalTestClient:
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
        self.sock.send((json.dumps(request) + "\n").encode())
        
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
            except:
                return None
        return None

def main():
    print("🎨 FINAL BRIGHT COLOR TEST")
    
    client = FinalTestClient(SOCKET_PATH)
    client.connect()
    
    try:
        # Create new project
        print("Creating bright test project...")
        client.send_request("goxel.create_project", ["BrightTest", 32, 32, 32])
        
        # Very bright colors
        red = [255, 0, 0, 255]      # Bright red
        green = [0, 255, 0, 255]    # Bright green  
        blue = [0, 0, 255, 255]     # Bright blue
        yellow = [255, 255, 0, 255] # Bright yellow
        
        print("Adding bright colored cubes...")
        
        # Red cube
        for x in range(0, 4):
            for y in range(0, 4):
                for z in range(0, 4):
                    client.send_request("goxel.add_voxel", [x, y, z] + red)
        
        # Green cube  
        for x in range(6, 10):
            for y in range(0, 4):
                for z in range(0, 4):
                    client.send_request("goxel.add_voxel", [x, y, z] + green)
        
        # Blue cube
        for x in range(0, 4):
            for y in range(6, 10):
                for z in range(0, 4):
                    client.send_request("goxel.add_voxel", [x, y, z] + blue)
        
        # Yellow cube
        for x in range(6, 10):
            for y in range(6, 10):
                for z in range(0, 4):
                    client.send_request("goxel.add_voxel", [x, y, z] + yellow)
        
        print("Added colorful cubes")
        
        # Save project
        client.send_request("goxel.save_project", ["./snoopy_test/bright_test.gox"])
        
        # Test different render settings
        print("Testing render with close camera...")
        
        # Very close camera
        result1 = client.send_request("goxel.render_scene", {
            "width": 600, 
            "height": 600,
            "camera": {
                "distance": 15,    # Very close
                "yaw": 30,         
                "pitch": -15
            },
            "output_path": "./snoopy_test/bright_close.png"
        })
        print(f"Close render: {result1}")
        
        # Medium distance
        result2 = client.send_request("goxel.render_scene", {
            "width": 600, 
            "height": 600,
            "camera": {
                "distance": 30,    
                "yaw": 45,         
                "pitch": -30
            },
            "output_path": "./snoopy_test/bright_medium.png"
        })
        print(f"Medium render: {result2}")
        
        # Far distance
        result3 = client.send_request("goxel.render_scene", {
            "width": 600, 
            "height": 600,
            "camera": {
                "distance": 60,    
                "yaw": 60,         
                "pitch": -45
            },
            "output_path": "./snoopy_test/bright_far.png"
        })
        print(f"Far render: {result3}")
        
        print("\n✅ Bright color test complete!")
        print("Check the following files:")
        print("- bright_close.png")
        print("- bright_medium.png") 
        print("- bright_far.png")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()