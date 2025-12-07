# FastAPI Rate-Limited Job Processing System

A backend system for handling job requests with rate limiting, fair scheduling, and idempotency support.

## 👨‍💻 Project Info

- **Student:** Abhishek Suryavanshi
- **Year:** 2nd Year
- **Tech Stack:** FastAPI, SQLAlchemy, MySQL, Pytest

## 🎯 Features

- ✅ **Fixed Window Rate Limiting** - Global and per-user limits
- ✅ **Idempotent Job Submission** - Prevents duplicate processing
- ✅ **Job Lifecycle Management** - States: queued → running → done/failed
- ✅ **Database Persistence** - All jobs stored in DB
- ✅ **Fair Scheduling** - FIFO order with last_served tracking
- ✅ **Background Worker** - Async job processing
- ✅ **Dashboard** - Real-time metrics and job monitoring
- ✅ **Restart Recovery** - Running jobs reset to queued on restart

## 📁 Project Structure

```
.
├── app/
│   ├── controllers/      # API endpoints
│   ├── core/            # Config & database
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── worker/          # Background worker
│   ├── main.py          # FastAPI app
│   └── test_suite.py    # Test cases
├── frontend/
│   └── index.html       # Dashboard UI
├── requirements.txt     # Dependencies
└── netlify.toml        # Deployment config
```

## 🚀 Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/Abhishek-surya/rate-limiting-ticket-queue.git
cd rate-limiting-ticket-queue
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
Create MySQL database:
```sql
CREATE DATABASE ticket_limiter;
```

### 5. Setup Environment Variables
Create `.env` file:
```
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ticket_limiter
```

## 🏃 Running the Application

### Start Backend
Make sure you're in the **project root directory**:
```bash
# From: rate-limiting-ticket-queue/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Optional)
From the **project root directory**:
```bash
# From: rate-limiting-ticket-queue/
python -m http.server 3000 --directory frontend
```

### Access URLs

**Local Development:**
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:3000

**Production Deployment:**
- **Backend API:** https://rate-limiting-ticket-queue-production.up.railway.app
- **API Docs:** https://rate-limiting-ticket-queue-production.up.railway.app/docs
- **Frontend Dashboard:** [Deployed on Netlify]

## 🧪 Running Tests

Make sure you're in the **project root directory**:

### Run All Tests
```bash
# From: rate-limiting-ticket-queue/
pytest app/test_suite.py -v
```

### Run Specific Test
```bash
pytest app/test_suite.py::TestRateLimiter -v
```

### Run Load Test
```bash
pytest app/test_suite.py::TestLoadTesting::test_load_100_requests -v
```

## 📊 Test Coverage

- **Unit Tests:** Rate limiting, Idempotency, Job states, Fair scheduling
- **Integration Tests:** Concurrent submissions, Fair ordering, Restart recovery, Dashboard
- **Load Tests:** 100 concurrent requests

## 🔧 Configuration

### Rate Limiting (app/core/config.py)
```python
WINDOW_SECONDS = 60        # Time window in seconds
GLOBAL_RATE_LIMIT = 5      # Max requests globally
PER_USER_RATE_LIMIT = 2    # Max requests per user
```

## 📡 API Endpoints

### Submit Job
```bash
POST /jobs/submit_job
{
  "user_id": "user_1",
  "payload": "test_data"
}
```

### Check Job Status
```bash
GET /jobs/job_status/{job_id}
```

### Dashboard
```bash
GET /jobs/dashboard
```

## 🎨 Dashboard Features

- Real-time job statistics
- Recent jobs list
- Job search by ID
- Auto-refresh every 5 seconds

## 🌐 Deployment

### Backend (Railway)
- Deployed at: https://rate-limiting-ticket-queue-production.up.railway.app

### Frontend (Netlify)
- Configured via `netlify.toml`
- Publish directory: `frontend`

## 📝 Key Design Decisions

1. **Fixed Window Rate Limiting** - Simple and stable approach
2. **Database-Driven Fairness** - No complex in-memory queues
3. **Idempotency via MD5 Hash** - Prevents duplicate job processing
4. **MySQL Database** - Reliable persistence and production-ready
5. **Single Background Worker** - Minimal complexity, can scale later

## 🔍 System Flow

```
Request → Rate Limit Check → Idempotency Check → 
Create Job (queued) → Worker Picks Job → 
Process (running) → Complete (done/failed)
```

## ⚠️ Known Limitations

- In-memory rate limiting (resets on restart)
- Single worker thread (can be scaled)
- Rate limiter can be moved to Redis for distributed systems

## 📄 License

Educational project - No license

## 📧 Contact

GitHub: [@Abhishek-surya](https://github.com/Abhishek-surya)
