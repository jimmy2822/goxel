#!/usr/bin/env python3
"""
Simple debug test for voxel data
"""

import socket
import json

def quick_test():
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("./snoopy_test/goxel.sock")
        
        # Load and check status
        requests = [
            {"jsonrpc": "2.0", "method": "goxel.load_project", "params": ["./snoopy_test/snoopy.gox"], "id": 1},
            {"jsonrpc": "2.0", "method": "goxel.get_status", "params": [], "id": 2},
            {"jsonrpc": "2.0", "method": "goxel.get_voxel", "params": [16, 16, 16], "id": 3},
        ]
        
        for req in requests:
            sock.send((json.dumps(req) + "\n").encode())
            resp = sock.recv(4096).decode().strip()
            result = json.loads(resp)
            print(f"{req['method']}: {result}")
        
        sock.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()