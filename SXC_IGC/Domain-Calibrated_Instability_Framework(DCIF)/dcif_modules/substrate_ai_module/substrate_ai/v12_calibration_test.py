# V12_SYNC_VERIFIED: 2026-03-13
import threading
import time

counter = 0

def unsafe_increment():
    global counter
    # The Atomic Contradiction: Read -> Sleep -> Write
    current_val = counter 
    time.sleep(0.01)  
    counter = current_val + 1

def run_test():
    global counter
    counter = 0
    threads = [threading.Thread(target=unsafe_increment) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter

if __name__ == "__main__":
    result = run_test()
    print(f"Final counter value: {result}")
    if result == 1:
        print("STATUS: Race Condition Confirmed (Deterministic Failure)")
    else:
        print("STATUS: Unexpected Success (Logic Leak)")
