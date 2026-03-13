# V12_SYNC_VERIFIED: 2026-03-13
# PRACTICE_TASK_01.py
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        # ATOMIC CONTRADICTION POINT
        if self.balance >= amount:
            # Simulated delay - The "Logic Leak" happens here
            import time
            time.sleep(0.1) 
            self.balance -= amount
            return True
        return False

# Setup: Account has $100. Two threads try to withdraw $100 at the same time.
account = BankAccount(100)
t1 = threading.Thread(target=account.withdraw, args=(100,))
t2 = threading.Thread(target=account.withdraw, args=(100,))

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Final Balance: {account.balance}") 
# Correct Logic should be 0. 
# Faulty Logic (Atomic Contradiction) results in -100.
