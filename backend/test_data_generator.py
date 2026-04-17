import time
import sys
import random

def generate_random_emg():
    return f"{random.randint(500, 1000)},{random.randint(500, 1000)},{random.randint(500, 1000)}\n"

def generate_emergency():
    return f"{random.randint(3100, 4000)},{random.randint(3100, 4000)},{random.randint(3100, 4000)}\n"

def generate_water():
    return f"{random.randint(500, 1000)},{random.randint(2100, 3000)},{random.randint(500, 1000)}\n"

def generate_hello():
    return f"{random.randint(2300, 3000)},{random.randint(500, 1200)},{random.randint(500, 1000)}\n"

if __name__ == "__main__":
    patterns = [generate_random_emg, generate_emergency, generate_random_emg, generate_water, generate_random_emg, generate_hello]
    print("Starting simulated sensor stream. Pipe to nc localhost 9000", file=sys.stderr)
    try:
        while True:
            pattern = random.choice(patterns)
            # Output line
            sys.stdout.write(pattern())
            sys.stdout.flush()
            time.sleep(1) # output 1 signal per second
    except KeyboardInterrupt:
        print("Stopping...", file=sys.stderr)
