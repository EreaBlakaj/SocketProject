import os
import sys

def shutdown_server():
    print("Serveri po mbyllet nga skripti shutdown.py...")
    # Shto këtu logjikën për të ndaluar shërbime të tjera, nëse nevojitet
    sys.exit(0)

if __name__ == "__main__":
    shutdown_server()