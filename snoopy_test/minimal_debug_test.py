#!/usr/bin/env python3

import socket
import json
import time

def test_framebuffer_debug():
    """Test the framebuffer debugging with minimal render"""
    
    try:
        # Connect to daemon
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/goxel.sock")
        
        print("🔍 FRAMEBUFFER DEBUG TEST")
        
        # Create a simple project
        create_request = {
            "jsonrpc": "2.0",
            "method": "goxel.create_project", 
            "params": ["DebugTest", 8, 8, 8],
            "id": 1
        }
        
        sock.send(json.dumps(create_request).encode() + b"\n")
        response_data = sock.recv(4096).decode().strip()
        response = json.loads(response_data)
        print(f"Create project: {response}")
        
        # Add one bright white voxel in center
        voxel_request = {
            "jsonrpc": "2.0",
            "method": "goxel.add_voxel",
            "params": [4, 4, 4, 255, 255, 255, 255],  # Bright white
            "id": 2
        }
        
        sock.send(json.dumps(voxel_request).encode() + b"\n")
        response_data = sock.recv(4096).decode().strip()
        response = json.loads(response_data)
        print(f"Add voxel: {response}")
        
        # Render with debugging - this should show the framebuffer analysis
        render_request = {
            "jsonrpc": "2.0",
            "method": "goxel.render_scene",
            "params": {
                "width": 400,
                "height": 300,
                "options": {
                    "return_mode": "file_path"
                }
            },
            "id": 3
        }
        
        sock.send(json.dumps(render_request).encode() + b"\n")
        response_data = sock.recv(8192).decode().strip()  # Larger buffer for debug info
        print(f"Raw response: {response_data[:200]}...")  # Show first 200 chars
        response = json.loads(response_data)
        print(f"Render response: {response}")
        
        if response.get('result') and response['result'].get('success'):
            file_info = response['result'].get('file', {})
            file_path = file_info.get('path', 'unknown')
            print(f"✅ Render successful! File saved to: {file_path}")
            print("📊 Check daemon console output for framebuffer analysis!")
        else:
            print(f"❌ Render failed: {response}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    test_framebuffer_debug()