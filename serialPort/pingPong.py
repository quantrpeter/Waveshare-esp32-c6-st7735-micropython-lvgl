import sys

while True:
    line = sys.stdin.readline().strip()
    if line == "ping":
        print("pong")