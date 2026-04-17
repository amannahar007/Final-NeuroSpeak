#!/usr/bin/env python3
"""
Health check script for NeuroSpeak backend
Verifies TCP server, HTTP server, and Socket.io endpoint are accessible
"""
import socket
import sys
import requests
from urllib.parse import urljoin

BACKEND_HOST = "localhost"
HTTP_PORT = 8000
TCP_PORT = 9000

def check_tcp_server():
    """Check if TCP server is listening on port 9000"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((BACKEND_HOST, TCP_PORT))
        sock.close()
        if result == 0:
            print(f"✓ TCP server is listening on {BACKEND_HOST}:{TCP_PORT}")
            return True
        else:
            print(f"✗ TCP server is NOT listening on {BACKEND_HOST}:{TCP_PORT}")
            return False
    except Exception as e:
        print(f"✗ Error checking TCP server: {e}")
        return False

def check_http_server():
    """Check if HTTP server is responding on port 8000"""
    try:
        url = f"http://{BACKEND_HOST}:{HTTP_PORT}/"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✓ HTTP server is responding on {BACKEND_HOST}:{HTTP_PORT}")
            return True
        else:
            print(f"✗ HTTP server returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking HTTP server: {e}")
        return False

def check_socketio_endpoint():
    """Check if Socket.io endpoint is accessible"""
    try:
        url = f"http://{BACKEND_HOST}:{HTTP_PORT}/socket.io/"
        response = requests.get(url, timeout=2)
        # Socket.io should return 400 for GET without proper handshake
        if response.status_code in [200, 400]:
            print(f"✓ Socket.io endpoint is accessible")
            return True
        else:
            print(f"✗ Socket.io endpoint returned unexpected status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking Socket.io endpoint: {e}")
        return False

def check_words_endpoint():
    """Check if /words API endpoint is accessible"""
    try:
        url = f"http://{BACKEND_HOST}:{HTTP_PORT}/words"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ /words endpoint is accessible ({len(data.get('words', []))} words configured)")
            return True
        else:
            print(f"✗ /words endpoint returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking /words endpoint: {e}")
        return False

def main():
    print("NeuroSpeak Backend Health Check")
    print("=" * 50)
    
    checks = [
        check_tcp_server(),
        check_http_server(),
        check_socketio_endpoint(),
        check_words_endpoint()
    ]
    
    print("=" * 50)
    if all(checks):
        print("✓ All checks passed!")
        sys.exit(0)
    else:
        print("✗ Some checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
