# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Git

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd scheme-platform
```

2. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Setup environment variables:
```bash
cp backend/.env.example backend/.env
# Edit .env with your local configuration
```

5. Start services:
```bash
docker-compose up -d
```

6. Run database migrations:
```bash
cd backend
alembic upgrade head
```

7. Start development servers:
```bash
# Backend (in backend directory)
uvicorn app.main:app --reload

# Frontend (in frontend directory)
npm start
```

## Project Structure

```
scheme-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── v1/         # API version 1
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── App.js
│   ├── Dockerfile
│   └── package.json
├── mobile/                 # Flutter mobile app
│   ├── lib/
│   ├── android/
│   ├── ios/
│   └── pubspec.yaml
├── ai-services/            # AI/ML microservices
│   ├── scheme-parser/      # Document parsing
│   ├── matching-engine/    # Eligibility matching
│   └── rag-service/        # RAG explanations
├── infrastructure/         # Infrastructure as Code
│   └── terraform/
│       ├── modules/
│       └── main.tf
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── docker-compose.yml
└── README.md
```

## Development Workflow

### Backend Development

#### Adding a New API Endpoint

1. Create schema in `backend/app/schemas/`:
```python
# backend/app/schemas/example.py
from pydantic import BaseModel

class ExampleRequest(BaseModel):
    name: str
    value: int

class ExampleResponse(BaseModel):
    id: str
    name: str
    value: int
```

2. Create route in `backend/app/api/v1/`:
```python
# backend/app/api/v1/example.py
from fastapi import APIRouter, Depends
from app.schemas.example import ExampleRequest, ExampleResponse

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(data: ExampleRequest):
    # Implementation
    pass
```

3. Register router in `main.py`:
```python
from app.api.v1 import example
app.include_router(example.router, prefix="/api/v1/example", tags=["Example"])
```

#### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

#### Running Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
pytest -v tests/test_specific.py  # Specific test
```

### Frontend Development

#### Component Structure

```javascript
// src/components/SchemeCard/SchemeCard.jsx
import React from 'react';
import './SchemeCard.css';

const SchemeCard = ({ scheme }) => {
  return (
    <div className="scheme-card">
      <h3>{scheme.name}</h3>
      <p>{scheme.description}</p>
    </div>
  );
};

export default SchemeCard;
```

#### API Integration

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

export const getSchemes = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/schemes`, { params });
  return response.data;
};
```

#### Running Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### AI Services Development

#### Scheme Parser Service

```python
# ai-services/scheme-parser/parser.py
import spacy
from transformers import pipeline

class SchemeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.classifier = pipeline("text-classification")
    
    def extract_eligibility(self, text: str) -> dict:
        doc = self.nlp(text)
        # Extract entities and rules
        rules = []
        for sent in doc.sents:
            if self._is_eligibility_sentence(sent):
                rules.append(self._parse_rule(sent))
        return {"rules": rules}
```

## Code Style and Standards

### Python (Backend)

Follow PEP 8 and use Black for formatting:
```bash
black backend/
flake8 backend/
mypy backend/
```

### JavaScript (Frontend)

Use ESLint and Prettier:
```bash
npm run lint
npm run format
```

### Commit Messages

Follow conventional commits:
```
feat: add scheme search functionality
fix: resolve authentication token expiry issue
docs: update API documentation
refactor: simplify matching engine logic
test: add tests for recommendation service
```

## Debugging

### Backend Debugging

1. Add breakpoints in VS Code
2. Use debug configuration:
```json
{
  "name": "Python: FastAPI",
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["app.main:app", "--reload"],
  "jinja": true
}
```

### Frontend Debugging

Use React DevTools and browser debugger:
```javascript
console.log('Debug:', data);
debugger;  // Breakpoint
```

### Database Debugging

```bash
# Connect to local PostgreSQL
docker-compose exec postgres psql -U postgres -d schemes_db

# View tables
\dt

# Query data
SELECT * FROM schemes LIMIT 10;
```

## Performance Testing

### Load Testing with Locust

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class SchemeUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_schemes(self):
        self.client.get("/api/v1/schemes")
    
    @task(3)
    def get_recommendations(self):
        self.client.get("/api/v1/recommendations")
```

Run load test:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Common Issues

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

## Useful Commands

### Docker

```bash
# View logs
docker-compose logs -f backend

# Rebuild containers
docker-compose up -d --build

# Clean up
docker-compose down -v
```

### Database

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres schemes_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres schemes_db < backup.sql
```

### AWS Local Testing

```bash
# Use LocalStack for AWS services
docker run -d -p 4566:4566 localstack/localstack

# Configure AWS CLI for LocalStack
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform Documentation](https://www.terraform.io/docs)
