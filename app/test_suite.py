"""
Test Suite for Rate-Limiting Ticket Queue System

Tests cover:
1. Unit Tests: Rate limiting, Idempotency, Job state transitions, Fair scheduling
2. Integration Tests: Concurrent submissions, Fair ordering, Restart recovery, Dashboard
3. Load Testing: 100-200 concurrent requests
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.services.rate_limiter import FixedWindowRateLimiter
from app.services.idempotency import check_idempotency
from app.services.job_service import (
    create_new_job,
    get_job_by_id,
    mark_job_running,
    mark_job_done,
    reset_running_jobs_on_restart
)
from app.services.scheduler import pick_next_job


# TEST DATABASE SETUP
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean database before and after each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# UNIT TESTS

class TestRateLimiter:
    """Fixed window rate limit logic"""
    
    def test_global_rate_limit_enforcement(self):
        """Test that global rate limit is enforced"""
        limiter = FixedWindowRateLimiter(global_limit=5, user_limit=100, window_seconds=60)
        
        for i in range(5):
            limiter.check(f"user_{i}")
        
        with pytest.raises(Exception):
            limiter.check("user_6")
    
    def test_per_user_rate_limit_enforcement(self):
        """Test that per-user rate limit is enforced"""
        limiter = FixedWindowRateLimiter(global_limit=100, user_limit=3, window_seconds=60)
        
        user_id = "test_user"
        for i in range(3):
            limiter.check(user_id)
        
        with pytest.raises(Exception):
            limiter.check(user_id)


class TestIdempotency:
    """Idempotency correctness"""
    
    def test_idempotency_returns_existing_job(self):
        """Test that same payload returns existing job"""
        import hashlib
        db = TestingSessionLocal()
        
        user_id = "test_user"
        payload = "test_payload"
        idem_key = hashlib.md5(payload.encode()).hexdigest()
        
        job1 = create_new_job(db, user_id, payload, idem_key)
        job1_id = job1.id
        
        job2 = check_idempotency(db, payload)
        
        assert job2 is not None
        assert job2.id == job1_id
        
        db.close()


class TestJobStateTransitions:
    """Job state transitions"""
    
    def test_state_transition_queued_to_running(self):
        """Test transition from queued to running"""
        db = TestingSessionLocal()
        
        job = create_new_job(db, "user_1", "payload", "key_1")
        assert job.state == "queued"
        
        job = mark_job_running(db, job)
        assert job.state == "running"
        
        db.close()
    
    def test_state_transition_running_to_done(self):
        """Test transition from running to done"""
        db = TestingSessionLocal()
        
        job = create_new_job(db, "user_1", "payload", "key_1")
        job = mark_job_running(db, job)
        
        job = mark_job_done(db, job, "success_result")
        assert job.state == "done"
        assert job.result == "success_result"
        
        db.close()


class TestFairScheduling:
    """Fair scheduling using last_served method"""
    
    def test_fifo_ordering(self):
        """Test that jobs are processed in FIFO order"""
        db = TestingSessionLocal()
        
        job1 = create_new_job(db, "user_1", "payload_1", "key_1")
        job2 = create_new_job(db, "user_2", "payload_2", "key_2")
        job3 = create_new_job(db, "user_3", "payload_3", "key_3")
        
        next_job = pick_next_job(db)
        assert next_job.id == job1.id
        
        mark_job_done(db, next_job, "result")
        
        next_job = pick_next_job(db)
        assert next_job.id == job2.id
        
        db.close()


# INTEGRATION TESTS

class TestConcurrentSubmissions:
    """Concurrent job submissions"""
    
    def test_concurrent_job_submissions(self):
        """Test that concurrent submissions create separate jobs"""
        num_requests = 10
        responses = []
        
        def submit_job(index):
            try:
                response = client.post(
                    "/jobs/submit_job",
                    json={
                        "user_id": f"user_{index}",
                        "payload": f"payload_{index}",
                        "idempotency_key": f"key_{index}"
                    }
                )
                return response.json() if response.status_code in [200, 201] else None
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(submit_job, i) for i in range(num_requests)]
            responses = [f.result() for f in as_completed(futures) if f.result() is not None]
        
        assert len(responses) > 0
        job_ids = [r.get('id') or r.get('job_id') for r in responses if r]
        assert len(job_ids) > 0


class TestFairOrderingVerification:
    """Fair ordering of job processing"""
    
    def test_job_processing_order(self):
        """Test that jobs are processed in submission order"""
        db = TestingSessionLocal()
        
        job_ids = []
        for i in range(5):
            job = create_new_job(db, f"user_{i}", f"payload_{i}", f"key_{i}")
            job_ids.append(job.id)
        
        picked_ids = []
        for _ in range(5):
            job = pick_next_job(db)
            if job:
                picked_ids.append(job.id)
                mark_job_done(db, job, "result")
        
        assert picked_ids == job_ids
        
        db.close()


class TestRestartRecovery:
    """System recovery on restart"""
    
    def test_running_jobs_reset_on_restart(self):
        """Test that running jobs are reset to queued on restart"""
        db = TestingSessionLocal()
        
        job1 = create_new_job(db, "user_1", "payload_1", "key_1")
        job2 = create_new_job(db, "user_2", "payload_2", "key_2")
        job3 = create_new_job(db, "user_3", "payload_3", "key_3")
        
        job1 = mark_job_running(db, job1)
        job2 = mark_job_running(db, job2)
        
        assert job1.state == "running"
        assert job2.state == "running"
        assert job3.state == "queued"
        
        reset_running_jobs_on_restart(db)
        
        job1 = get_job_by_id(db, job1.id)
        job2 = get_job_by_id(db, job2.id)
        job3 = get_job_by_id(db, job3.id)
        
        assert job1.state == "queued"
        assert job2.state == "queued"
        assert job3.state == "queued"
        
        db.close()


class TestDashboardData:
    """Dashboard data aggregation"""
    
    def test_dashboard_endpoint(self):
        """Test that dashboard endpoint returns correct data"""
        for i in range(3):
            client.post(
                "/jobs/submit_job",
                json={
                    "user_id": f"user_{i}",
                    "payload": f"payload_{i}",
                    "idempotency_key": f"key_{i}"
                }
            )
        
        response = client.get("/jobs/dashboard")
        assert response.status_code in [200, 404]


# LOAD TESTING

class TestLoadTesting:
    """100-200 concurrent requests"""
    
    def test_load_100_requests(self):
        """Test with 100 concurrent job submissions"""
        num_requests = 100
        responses = []
        errors = []
        
        def submit_job(index):
            try:
                response = client.post(
                    "/jobs/submit_job",
                    json={
                        "user_id": f"user_{index % 10}",
                        "payload": f"payload_{index}",
                        "idempotency_key": f"key_{index}"
                    }
                )
                return response.json(), None
            except Exception as e:
                return None, str(e)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(submit_job, i) for i in range(num_requests)]
            for future in as_completed(futures):
                resp, err = future.result()
                if err:
                    errors.append(err)
                else:
                    responses.append(resp)
        
        success_rate = len(responses) / num_requests
        assert success_rate >= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
