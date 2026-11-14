"""
Asynchronous Reasoning Job Queue Architecture

This implements the architecture where:
- Simulation owns the queue
- LLM is treated like a GPU (external resource)
- Simulation never waits indefinitely for LLM
- Jobs remain pending if LLM hangs
"""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
from enum import Enum
import uuid

from llm_service import LLMService, LLMRequest, LLMResponse


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ReasoningJob:
    """A single reasoning job in the queue."""
    job_id: str
    entity_id: str
    tick: int
    request: LLMRequest
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[LLMResponse] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mark_processing(self):
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now(timezone.utc)
    
    def mark_completed(self, result: LLMResponse):
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
    
    def mark_failed(self, error: str):
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error
    
    def mark_timeout(self):
        self.status = JobStatus.TIMEOUT
        self.completed_at = datetime.now(timezone.utc)
        self.error = "Job timed out"


@dataclass
class ReasoningQueue:
    """Asynchronous reasoning queue owned by simulation."""
    
    llm_service: LLMService = field(default_factory=LLMService)
    max_concurrent_jobs: int = 3
    job_timeout_seconds: int = 120
    
    # Job storage
    pending_jobs: Dict[str, ReasoningJob] = field(default_factory=dict)
    processing_jobs: Dict[str, ReasoningJob] = field(default_factory=dict)
    completed_jobs: Dict[str, ReasoningJob] = field(default_factory=dict)
    
    # Worker thread
    _worker_thread: Optional[threading.Thread] = None
    _running: bool = False
    _job_added_event: threading.Event = threading.Event()
    
    def start_worker(self):
        """Start the background worker thread."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._running = True
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
            print("  ✓ Reasoning worker started")
    
    def stop_worker(self):
        """Stop the background worker thread."""
        self._running = False
        self._job_added_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            print("  ✓ Reasoning worker stopped")
    
    def submit_job(self, entity_id: str, tick: int, request: LLMRequest, metadata: Dict[str, Any] = None) -> str:
        """Submit a reasoning job to the queue."""
        job_id = str(uuid.uuid4())
        job = ReasoningJob(
            job_id=job_id,
            entity_id=entity_id,
            tick=tick,
            request=request,
            metadata=metadata or {}
        )
        self.pending_jobs[job_id] = job
        self._job_added_event.set()
        return job_id
    
    def get_job_result(self, job_id: str, timeout: float = 0.0) -> Optional[LLMResponse]:
        """Get job result if available, return None if not ready."""
        if job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
            if job.result:
                return job.result
        return None
    
    def _worker_loop(self):
        """Background worker that processes jobs from the queue."""
        while self._running:
            # Wait for jobs or timeout
            self._job_added_event.wait(timeout=1.0)
            self._job_added_event.clear()
            
            # Process jobs if available
            if len(self.processing_jobs) < self.max_concurrent_jobs and self.pending_jobs:
                # Move a job from pending to processing
                job_id, job = next(iter(self.pending_jobs.items()))
                del self.pending_jobs[job_id]
                self.processing_jobs[job_id] = job
                job.mark_processing()
                
                # Process the job
                try:
                    result = self.llm_service.invoke(job.request)
                    job.mark_completed(result)
                    self.completed_jobs[job_id] = job
                    del self.processing_jobs[job_id]
                except Exception as e:
                    job.mark_failed(str(e))
                    self.completed_jobs[job_id] = job
                    del self.processing_jobs[job_id]
    
    def process_job(self, job: ReasoningJob) -> LLMResponse:
        """Process a single job synchronously (for testing)."""
        job.mark_processing()
        try:
            result = self.llm_service.invoke(job.request)
            job.mark_completed(result)
            self.completed_jobs[job.job_id] = job
            return result
        except Exception as e:
            job.mark_failed(str(e))
            self.completed_jobs[job.job_id] = job
            raise
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status."""
        return {
            "pending": len(self.pending_jobs),
            "processing": len(self.processing_jobs),
            "completed": len(self.completed_jobs)
        }
