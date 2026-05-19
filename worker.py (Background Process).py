from scheduler import PostScheduler
import time
import signal
import sys

def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting English Learning FB Bot Worker...")
    scheduler = PostScheduler()
    scheduler.start()
    
    # Keep alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nWorker stopped")
        scheduler.stop()