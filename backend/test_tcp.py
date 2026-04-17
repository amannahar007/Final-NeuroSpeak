import socket, time
try:
    print("Connecting to backend...", flush=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9000))
    time.sleep(1)
    s.sendall(b"3500,3500,3500\n")
    print("Sent EMERGENCY", flush=True)
    time.sleep(1)
    s.sendall(b"1000,2500,1000\n")
    print("Sent WATER", flush=True)
    time.sleep(1)
    s.sendall(b"2500,1000,1000\n")
    print("Sent HELLO", flush=True)
    time.sleep(1)
    s.close()
    print("Test tcp stream finished.", flush=True)
except Exception as e:
    print(f"Error: {e}")
