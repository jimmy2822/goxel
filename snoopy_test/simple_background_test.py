#!/usr/bin/env python3

import socket
import json
import time

def test_background_color():
    """Simple test for background color parameter"""
    
    try:
        # Connect to daemon
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/goxel.sock")
        
        print("🎨 BACKGROUND COLOR TEST")
        
        # Create project
        create_req = {"jsonrpc": "2.0", "method": "goxel.create_project", "params": ["BGTest", 8, 8, 8], "id": 1}
        sock.send(json.dumps(create_req).encode() + b"\n")
        create_resp = json.loads(sock.recv(4096).decode().strip())
        print(f"✅ Project created: {create_resp['result']['success']}")
        
        # Add a bright red voxel
        voxel_req = {"jsonrpc": "2.0", "method": "goxel.add_voxel", "params": [4, 4, 4, 255, 0, 0, 255], "id": 2}
        sock.send(json.dumps(voxel_req).encode() + b"\n")
        voxel_resp = json.loads(sock.recv(4096).decode().strip())  
        print(f"✅ RED voxel added: {voxel_resp['result']['success']}")
        
        sock.close()  # Close first connection
        print("🔌 Closed first connection")
        
        # Open new connection for render (avoid any buffering issues)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) 
        sock.connect("/tmp/goxel.sock")
        
        # Render with BLACK background
        render_req = {
            "jsonrpc": "2.0",
            "method": "goxel.render_scene", 
            "params": {
                "width": 400, 
                "height": 300,
                "options": {
                    "return_mode": "file_path",
                    "background_color": [0, 0, 0, 255]  # BLACK background
                }
            },
            "id": 1
        }
        
        sock.send(json.dumps(render_req).encode() + b"\n")
        render_resp = json.loads(sock.recv(8192).decode().strip())
        
        if render_resp.get('result', {}).get('success'):
            file_path = render_resp['result']['file']['path']
            print(f"🎯 RENDER SUCCESS: {file_path}")
            print("📊 Check daemon output - should show BLACK background: [0,0,0,255]!")
        else:
            print(f"❌ Render failed: {render_resp}")
            
        sock.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    test_background_color()