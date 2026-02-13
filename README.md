# AI-Powered Government Scheme Recommendation Platform

A production-ready, scalable platform that helps rural Indian citizens discover and access government schemes they're eligible for using AI-powered matching and multilingual support.

## 🎯 Project Vision

Bridge the information gap between government welfare schemes and rural citizens through intelligent, personalized recommendations powered by AI and cloud infrastructure.

## 🏗️ Architecture

- **Cloud Provider**: AWS
- **Backend**: Python (FastAPI) + Node.js microservices
- **Frontend**: React Web + Flutter Mobile
- **AI/ML**: NLP for scheme parsing, RAG for explanations
- **Database**: PostgreSQL (RDS) + DynamoDB
- **Infrastructure**: Terraform, Docker, ECS

## 📁 Project Structure

```
/backend          - API services and business logic
/frontend         - React web application
/mobile           - Flutter mobile app
/ai-services      - AI/ML microservices
/infrastructure   - Terraform IaC
/docs             - Documentation
/scripts          - Deployment and utility scripts
```

## 🚀 Quick Start

See [docs/development.md](docs/development.md) for local setup instructions.

## 📚 Documentation

- [Requirements](docs/requirements.md) - Functional and non-functional requirements
- [System Design](docs/design.md) - Architecture and technical design
- [API Documentation](docs/api.md) - API endpoints and contracts
- [Deployment Guide](docs/deployment.md) - AWS deployment instructions

## 🔐 Security

- AWS Cognito authentication
- IAM role-based access control
- Encrypted data at rest and in transit
- HTTPS only via ACM

## 📊 Performance Targets

- Support 100k concurrent users
- API response time < 500ms
- 99.9% uptime SLA
- Scalable to pan-India deployment

## 📝 License

[Add appropriate license]
