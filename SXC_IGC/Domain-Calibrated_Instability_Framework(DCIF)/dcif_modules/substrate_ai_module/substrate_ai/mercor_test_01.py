# V12_SYNC_VERIFIED: 2026-03-13
import threading
import time

class MercorResourceManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.resources = {"A": True, "B": True}
        self.active_leases = {}

    def acquire_lease(self, client_id, resource_id):
        with self.lock:  # <--- The Logic Gate
            if self.resources.get(resource_id):
                time.sleep(0.01)  # Context switch is now protected
                self.resources[resource_id] = False
                self.active_leases[client_id] = resource_id
                return True
            return False

# TEST HARNESS
def simulate_mercor_task():
    manager = MercorResourceManager()
    results = []

    def task(cid):
        if manager.acquire_lease(cid, "A"):
            results.append(f"SUCCESS_{cid}")

    threads = [threading.Thread(target=task, args=(i,)) for i in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()

    # If both succeeded, the logic failed (Only one lease should exist)
    return results

if __name__ == "__main__":
    print(f"Audit Results: {simulate_mercor_task()}")
