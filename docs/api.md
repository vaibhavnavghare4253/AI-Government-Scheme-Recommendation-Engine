# API Documentation

## Base URL
```
Production: https://api.schemes.gov.in
Development: http://localhost:8000
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone_number": "+919876543210"
}

Response: 200 OK
{
  "message": "OTP sent successfully",
  "session_id": "uuid"
}
```

#### Verify OTP
```http
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "session_id": "uuid",
  "otp": "123456"
}

Response: 200 OK
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### User Profile

#### Get Profile
```http
GET /api/v1/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "full_name": "John Doe",
  "age": 35,
  "gender": "male",
  "annual_income": 150000,
  "state": "Maharashtra",
  "district": "Pune",
  ...
}
```

#### Create/Update Profile
```http
POST /api/v1/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "age": 35,
  "gender": "male",
  "annual_income": 150000,
  "caste_category": "OBC",
  "state": "Maharashtra",
  "district": "Pune",
  "occupation": "Farmer",
  "family_size": 4,
  "is_bpl": false,
  "has_disability": false,
  "preferred_language": "mr"
}

Response: 200 OK
{
  "id": "uuid",
  "message": "Profile updated successfully"
}
```

### Schemes

#### List Schemes
```http
GET /api/v1/schemes?skip=0&limit=10&state=Maharashtra&category=Agriculture

Response: 200 OK
{
  "total": 150,
  "skip": 0,
  "limit": 10,
  "schemes": [
    {
      "id": "uuid",
      "scheme_code": "PM-KISAN",
      "name": "Pradhan Mantri Kisan Samman Nidhi",
      "description": "Financial support to farmers",
      "benefit_amount": 6000,
      "category": "Agriculture",
      "is_central": true,
      ...
    }
  ]
}
```

#### Get Scheme Details
```http
GET /api/v1/schemes/{scheme_id}

Response: 200 OK
{
  "id": "uuid",
  "scheme_code": "PM-KISAN",
  "name": "Pradhan Mantri Kisan Samman Nidhi",
  "description": "...",
  "eligibility_rules": [
    {
      "rule_type": "land_ownership",
      "operator": "<=",
      "value_max": 2.0
    }
  ],
  ...
}
```

#### Search Schemes
```http
GET /api/v1/schemes/search?q=farmer&skip=0&limit=10

Response: 200 OK
{
  "total": 25,
  "schemes": [...]
}
```

### Recommendations

#### Get Recommendations
```http
GET /api/v1/recommendations
Authorization: Bearer <token>

Response: 200 OK
{
  "recommendations": [
    {
      "id": "uuid",
      "scheme": {
        "id": "uuid",
        "name": "PM-KISAN",
        ...
      },
      "match_score": 95.5,
      "explanation": "You are eligible because...",
      "document_checklist": [
        "Aadhaar Card",
        "Land Records",
        "Bank Account Details"
      ]
    }
  ]
}
```

#### Refresh Recommendations
```http
POST /api/v1/recommendations/refresh
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Recommendations refreshed",
  "count": 12
}
```

#### Submit Feedback
```http
POST /api/v1/recommendations/{recommendation_id}/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "rating": 5,
  "comment": "Very helpful",
  "applied": true
}

Response: 200 OK
{
  "message": "Feedback submitted"
}
```

### Admin

#### Upload Scheme
```http
POST /api/v1/admin/schemes
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "scheme_code": "NEW-SCHEME-001",
  "name": "New Scheme",
  "description": "...",
  "category": "Education",
  "benefit_amount": 10000,
  ...
}

Response: 201 Created
{
  "id": "uuid",
  "message": "Scheme created successfully"
}
```

#### Upload Document
```http
POST /api/v1/admin/schemes/{scheme_id}/documents
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <pdf_file>

Response: 200 OK
{
  "document_id": "uuid",
  "status": "processing"
}
```

#### Get Analytics
```http
GET /api/v1/admin/analytics?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "total_users": 50000,
  "active_users": 35000,
  "total_schemes": 250,
  "recommendations_generated": 150000,
  "top_schemes": [
    {
      "scheme_id": "uuid",
      "name": "PM-KISAN",
      "recommendation_count": 25000
    }
  ],
  "district_analytics": [...]
}
```

### Voice

#### Transcribe Audio
```http
POST /api/v1/voice/transcribe
Authorization: Bearer <token>
Content-Type: multipart/form-data

audio: <audio_file>
language: hi

Response: 200 OK
{
  "text": "मुझे किसान योजना के बारे में जानकारी चाहिए",
  "language": "hi"
}
```

#### Synthesize Speech
```http
POST /api/v1/voice/synthesize
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "You are eligible for PM-KISAN scheme",
  "language": "en"
}

Response: 200 OK
{
  "audio_url": "https://s3.../audio.mp3"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "age",
      "message": "Age must be between 18 and 100"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limits

- Authenticated users: 1000 requests/minute
- Unauthenticated: 100 requests/minute
- Admin users: 5000 requests/minute

## Pagination

List endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10, max: 100)

## Filtering

Schemes can be filtered by:
- `state`: State name
- `category`: Scheme category
- `is_active`: Active status (true/false)
- `is_central`: Central vs State scheme

## Localization

All text fields support multiple languages:
- `name`, `name_hi`, `name_mr`, `name_ta`
- `description`, `description_hi`, `description_mr`, `description_ta`

Use `Accept-Language` header to specify preferred language:
```
Accept-Language: hi
```
