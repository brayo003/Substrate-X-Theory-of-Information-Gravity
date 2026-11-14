"""
Test the asynchronous reasoning queue architecture.
"""

from reasoning_queue import ReasoningQueue, ReasoningJob, JobStatus
from llm_service import LLMService, LLMRequest

print("=" * 60)
print("ASYNCHRONOUS REASONING QUEUE TEST")
print("=" * 60)

print("\n[1] Creating reasoning queue...")
queue = ReasoningQueue()
print("  ✓ Queue created")

print("\n[2] Starting worker...")
queue.start_worker()

print("\n[3] Submitting jobs...")
# Submit multiple jobs to test the queue
jobs = []
for i in range(3):
    prompt = f"""You are Aria, a villager. Your hunger is {0.5 + i * 0.1}. What should you do?"""
    request = LLMRequest(prompt=prompt, timeout=60)
    job_id = queue.submit_job(
        entity_id="aria",
        tick=100 + i,
        request=request,
        metadata={"test": True}
    )
    jobs.append(job_id)
    print(f"  ✓ Job {i+1} submitted: {job_id}")

print("\n[4] Waiting for jobs to complete...")
import time
time.sleep(30)  # Wait for jobs to process

print("\n[5] Checking job results...")
for i, job_id in enumerate(jobs):
    result = queue.get_job_result(job_id)
    if result:
        print(f"  Job {i+1}: Success={result.success}")
        print(f"    Response: {result.text[:100]}...")
    else:
        print(f"  Job {i+1}: Not ready")

print("\n[6] Queue status:")
status = queue.get_queue_status()
print(f"  Pending: {status['pending']}")
print(f"  Processing: {status['processing']}")
print(f"  Completed: {status['completed']}")

print("\n[7] Stopping worker...")
queue.stop_worker()

print("\n" + "=" * 60)
print("ASYNCHRONOUS QUEUE TEST COMPLETE")
print("=" * 60)
