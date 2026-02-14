# System Design Document

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Web Browser │  │ Mobile App   │  │ Voice IVR    │          │
│  │   (React)    │  │  (Flutter)   │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  CloudFront CDN │
                    │   (Static +     │
                    │   API Cache)    │
                    └────────┬────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────▼─────────┐              ┌───────────▼──────────┐
│  API Gateway      │              │  AWS Cognito         │
│  - Rate Limiting  │              │  - Authentication    │
│  - Request Valid. │              │  - User Pools        │
│  - CORS           │              │  - JWT Tokens        │
└─────────┬─────────┘              └──────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (ECS)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Backend    │  │  AI Service  │  │    Admin     │         │
│  │   API        │  │  - Matching  │  │   Service    │         │
│  │  (FastAPI)   │  │  - NLP       │  │              │         │
│  │              │  │  - RAG       │  │              │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  RDS         │  │  DynamoDB    │  │  S3 Buckets  │          │
│  │ (PostgreSQL) │  │  - Sessions  │  │  - Documents │          │
│  │ - Users      │  │  - Cache     │  │  - Assets    │          │
│  │ - Schemes    │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ OpenSearch   │  │  Vector DB   │  │     SQS      │          │
│  │ - Search     │  │  (Pinecone/  │  │  - Async     │          │
│  │ - Analytics  │  │   pgvector)  │  │    Jobs      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    AI/ML SERVICES                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Bedrock    │  │  Translate   │  │    Polly     │           │
│  │   (LLM)      │  │              │  │   (TTS)      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │  Transcribe  │  │  Comprehend  │                             │
│  │   (STT)      │  │   (NLP)      │                             │
│  └──────────────┘  └──────────────┘                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 MONITORING & OPERATIONS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ CloudWatch   │  │  X-Ray       │  │  CloudTrail  │           │
│  │ - Logs       │  │ - Tracing    │  │  - Audit     │           │
│  │ - Metrics    │  │              │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
```

## 2. AWS Service Mapping

| Component | AWS Service | Purpose |
|-----------|-------------|---------|
| Frontend Hosting | S3 + CloudFront | Static web hosting with CDN |
| API Gateway | API Gateway | REST API management, rate limiting |
| Authentication | Cognito | User authentication and authorization |
| Backend Compute | ECS Fargate | Containerized application hosting |
| Database | RDS PostgreSQL | Primary relational database |
| Cache/Sessions | DynamoDB | Fast key-value storage |
| File Storage | S3 | Document and asset storage |
| Search | OpenSearch | Full-text search and analytics |
| Message Queue | SQS | Async job processing |
| LLM | Bedrock | AI-powered explanations |
| Translation | Translate | Multilingual support |
| Text-to-Speech | Polly | Voice output |
| Speech-to-Text | Transcribe | Voice input |
| NLP | Comprehend | Entity extraction |
| Monitoring | CloudWatch | Logs, metrics, alarms |
| Tracing | X-Ray | Distributed tracing |
| Secrets | Secrets Manager | API keys, credentials |
| DNS | Route 53 | Domain management |
| SSL/TLS | ACM | Certificate management |
| Load Balancing | ALB | Application load balancing |

## 3. Database Schema Design

### 3.1 PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- User profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    age INTEGER,
    gender VARCHAR(20),
    annual_income DECIMAL(12, 2),
    caste_category VARCHAR(50),
    state VARCHAR(100),
    district VARCHAR(100),
    block VARCHAR(100),
    village VARCHAR(100),
    occupation VARCHAR(100),
    family_size INTEGER,
    is_bpl BOOLEAN,
    has_disability BOOLEAN,
    education_level VARCHAR(50),
    land_ownership DECIMAL(10, 2),
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schemes
CREATE TABLE schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    name_hi TEXT,
    name_mr TEXT,
    name_ta TEXT,
    description TEXT,
    description_hi TEXT,
    description_mr TEXT,
    description_ta TEXT,
    department VARCHAR(255),
    category VARCHAR(100),
    benefit_type VARCHAR(100),
    benefit_amount DECIMAL(12, 2),
    state VARCHAR(100),
    is_central BOOLEAN DEFAULT false,
    application_url TEXT,
    document_url TEXT,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Eligibility rules (structured)
CREATE TABLE eligibility_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id UUID REFERENCES schemes(id) ON DELETE CASCADE,
    rule_type VARCHAR(50), -- age, income, gender, location, etc.
    operator VARCHAR(20), -- >, <, =, IN, BETWEEN
    value_min DECIMAL(12, 2),
    value_max DECIMAL(12, 2),
    value_list TEXT[], -- for IN operator
    is_mandatory BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scheme_id UUID REFERENCES schemes(id) ON DELETE CASCADE,
    match_score DECIMAL(5, 2),
    explanation TEXT,
    explanation_hi TEXT,
    explanation_mr TEXT,
    explanation_ta TEXT,
    document_checklist JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMP,
    applied_at TIMESTAMP
);

-- User interactions
CREATE TABLE user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scheme_id UUID REFERENCES schemes(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50), -- view, click, apply, feedback
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin users
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'admin', -- admin, superadmin
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scheme documents
CREATE TABLE scheme_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id UUID REFERENCES schemes(id) ON DELETE CASCADE,
    s3_key VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size BIGINT,
    processing_status VARCHAR(50) DEFAULT 'pending',
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_schemes_active ON schemes(is_active);
CREATE INDEX idx_schemes_state ON schemes(state);
CREATE INDEX idx_eligibility_scheme ON eligibility_rules(scheme_id);
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_scheme ON recommendations(scheme_id);
CREATE INDEX idx_interactions_user ON user_interactions(user_id);
```

### 3.2 DynamoDB Tables

**Table: user-sessions**
- Partition Key: session_id (String)
- Attributes: user_id, cognito_id, expires_at, metadata
- TTL: expires_at

**Table: scheme-cache**
- Partition Key: cache_key (String)
- Attributes: data, ttl
- TTL: ttl

## 4. API Design

### 4.1 Authentication APIs

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/verify-otp
POST /api/v1/auth/refresh-token
POST /api/v1/auth/logout
```

### 4.2 User Profile APIs

```
GET    /api/v1/profile
POST   /api/v1/profile
PUT    /api/v1/profile
DELETE /api/v1/profile
```

### 4.3 Scheme APIs

```
GET    /api/v1/schemes              # List all schemes
GET    /api/v1/schemes/:id          # Get scheme details
GET    /api/v1/schemes/search       # Search schemes
GET    /api/v1/schemes/categories   # Get categories
```

### 4.4 Recommendation APIs

```
GET    /api/v1/recommendations      # Get user recommendations
POST   /api/v1/recommendations/refresh  # Recalculate
GET    /api/v1/recommendations/:id  # Get recommendation details
POST   /api/v1/recommendations/:id/feedback  # Submit feedback
```

### 4.5 Admin APIs

```
POST   /api/v1/admin/schemes        # Create scheme
PUT    /api/v1/admin/schemes/:id    # Update scheme
DELETE /api/v1/admin/schemes/:id    # Delete scheme
POST   /api/v1/admin/schemes/:id/documents  # Upload document
GET    /api/v1/admin/analytics      # Get analytics
GET    /api/v1/admin/users          # List users
```

### 4.6 Voice APIs

```
POST   /api/v1/voice/transcribe     # Speech to text
POST   /api/v1/voice/synthesize     # Text to speech
```

### 4.7 Translation APIs

```
POST   /api/v1/translate            # Translate text
```

## 5. AI Pipeline Design

### 5.1 Scheme Document Processing Pipeline

```
┌─────────────┐
│ Admin       │
│ Uploads PDF │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ S3 Bucket   │
│ (Documents) │
└──────┬──────┘
       │ (S3 Event)
       ▼
┌─────────────┐
│ Lambda      │
│ Trigger     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Text        │
│ Extraction  │
│ (Textract)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ NLP Model   │
│ - Extract   │
│   Rules     │
│ - Identify  │
│   Entities  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Structured  │
│ Rules       │
│ (JSON)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Store in    │
│ RDS         │
└─────────────┘
```

### 5.2 Eligibility Matching Engine

**Layer 1: Rule-Based Filtering**
```python
def filter_schemes(user_profile, all_schemes):
    eligible = []
    for scheme in all_schemes:
        rules = get_eligibility_rules(scheme.id)
        if evaluate_rules(user_profile, rules):
            eligible.append(scheme)
    return eligible
```

**Layer 2: AI Ranking**
```python
def rank_schemes(user_profile, eligible_schemes):
    features = extract_features(user_profile, eligible_schemes)
    scores = ml_model.predict(features)
    ranked = sort_by_score(eligible_schemes, scores)
    return ranked[:10]
```

### 5.3 RAG-Based Explanation Engine

```
┌─────────────┐
│ User +      │
│ Scheme      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Retrieve    │
│ Scheme Docs │
│ from Vector │
│ DB          │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Build       │
│ Context     │
│ Prompt      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Bedrock LLM │
│ Generate    │
│ Explanation │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Return      │
│ - Why       │
│ - Checklist │
│ - Steps     │
└─────────────┘
```

## 6. Deployment Architecture

### 6.1 Multi-AZ Deployment

```
Region: ap-south-1 (Mumbai)

┌─────────────────────────────────────────────────────────┐
│                         VPC                              │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │   AZ-1a          │      │   AZ-1b          │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │ Public     │  │      │  │ Public     │  │        │
│  │  │ Subnet     │  │      │  │ Subnet     │  │        │
│  │  │ - NAT GW   │  │      │  │ - NAT GW   │  │        │
│  │  │ - ALB      │  │      │  │ - ALB      │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │ Private    │  │      │  │ Private    │  │        │
│  │  │ Subnet     │  │      │  │ Subnet     │  │        │
│  │  │ - ECS      │  │      │  │ - ECS      │  │        │
│  │  │ - Lambda   │  │      │  │ - Lambda   │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │ Data       │  │      │  │ Data       │  │        │
│  │  │ Subnet     │  │      │  │ Subnet     │  │        │
│  │  │ - RDS      │  │      │  │ - RDS      │  │        │
│  │  │   Primary  │  │      │  │   Standby  │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Auto-Scaling Configuration

**ECS Service Auto-Scaling:**
- Target CPU: 70%
- Target Memory: 80%
- Min tasks: 2
- Max tasks: 50
- Scale-out cooldown: 60s
- Scale-in cooldown: 300s

**RDS Read Replicas:**
- Auto-create when read IOPS > 80%
- Max replicas: 5

## 7. Security Architecture

### 7.1 Network Security
- VPC with public/private subnets
- Security groups with least privilege
- NACLs for subnet-level filtering
- WAF rules on API Gateway and ALB
- DDoS protection via Shield Standard

### 7.2 Application Security
- JWT tokens with 1-hour expiry
- Refresh tokens with 30-day expiry
- API rate limiting: 1000 req/min per user
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection (CSP headers)

### 7.3 Data Security
- RDS encryption at rest (AES-256)
- S3 encryption at rest (SSE-S3)
- TLS 1.3 for data in transit
- Secrets in AWS Secrets Manager
- IAM roles for service-to-service auth

## 8. Cost Estimation (Monthly)

### 8.1 Compute
- ECS Fargate (4 vCPU, 8GB): $150
- Lambda (1M invocations): $20
- Total: $170

### 8.2 Database
- RDS db.t3.medium (Multi-AZ): $120
- DynamoDB (on-demand): $50
- OpenSearch t3.small: $80
- Total: $250

### 8.3 Storage
- S3 (100GB): $3
- RDS storage (100GB): $12
- Total: $15

### 8.4 Networking
- CloudFront (1TB): $85
- ALB: $25
- Data transfer: $50
- Total: $160

### 8.5 AI Services
- Bedrock (Claude): $100
- Translate: $30
- Polly: $20
- Transcribe: $20
- Total: $170

### 8.6 Other
- Cognito: $10
- CloudWatch: $20
- Secrets Manager: $5
- Total: $35

**Grand Total: ~$800/month** (for 10k active users)

## 9. Scalability Strategy

### 9.1 Horizontal Scaling
- ECS auto-scaling based on CPU/memory
- Lambda concurrent execution limits
- Read replicas for database

### 9.2 Caching Strategy
- CloudFront for static assets (1-day TTL)
- API Gateway caching (5-min TTL)
- DynamoDB for session cache
- Application-level caching (Redis if needed)

### 9.3 Database Optimization
- Connection pooling
- Query optimization and indexing
- Partitioning large tables
- Archival of old data

## 10. Failure Handling

### 10.1 Retry Logic
- Exponential backoff for API calls
- SQS dead-letter queues
- Circuit breaker pattern

### 10.2 Graceful Degradation
- Serve cached recommendations if AI service down
- Basic search if OpenSearch unavailable
- Queue async jobs if processing fails

### 10.3 Monitoring and Alerts
- CloudWatch alarms for:
  - High error rates (> 1%)
  - High latency (> 1s)
  - Low success rate (< 99%)
  - Database connections (> 80%)
- PagerDuty integration for critical alerts

## 11. Future Enhancements

### Phase 2
- Mobile app (Flutter)
- Aadhaar integration
- DigiLocker integration
- Advanced analytics dashboard

### Phase 3
- Blockchain-based verification
- Direct application submission
- Payment gateway integration
- Chatbot interface

### Phase 4
- Predictive analytics (missed benefits)
- District-level impact heatmaps
- Multi-tenant architecture for states
- Offline-first mobile app
