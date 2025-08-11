#!/usr/bin/env python3

import socket
import json

def test_high_contrast():
    """Test with bright red voxel against dark background for maximum visibility"""
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/goxel.sock")
        
        print("🔥 HIGH CONTRAST VOXEL TEST")
        
        # Create project
        create_request = {
            "jsonrpc": "2.0",
            "method": "goxel.create_project", 
            "params": ["ContrastTest", 8, 8, 8],
            "id": 1
        }
        
        sock.send(json.dumps(create_request).encode() + b"\n")
        response_data = sock.recv(4096).decode().strip()
        response = json.loads(response_data)
        print(f"✅ Project created: {response['result']['success']}")
        
        # Add BRIGHT RED voxel (maximum contrast)
        voxel_request = {
            "jsonrpc": "2.0",
            "method": "goxel.add_voxel",
            "params": [4, 4, 4, 255, 0, 0, 255],  # BRIGHT RED
            "id": 2
        }
        
        sock.send(json.dumps(voxel_request).encode() + b"\n")
        response_data = sock.recv(4096).decode().strip()
        response = json.loads(response_data)
        print(f"✅ RED voxel added: {response['result']['success']}")
        
        # Render with BLACK background for maximum contrast
        render_request = {
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
            "id": 3
        }
        
        sock.send(json.dumps(render_request).encode() + b"\n")
        response_data = sock.recv(8192).decode().strip()
        response = json.loads(response_data)
        
        if response.get('result') and response['result'].get('success'):
            file_path = response['result']['file']['path']
            print(f"🎨 HIGH CONTRAST RENDER: {file_path}")
            print("📊 Check daemon output for pixel analysis!")
            print("🔍 This should show RED voxel pixels vs BLACK background!")
        else:
            print(f"❌ Render failed: {response}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    test_high_contrast()