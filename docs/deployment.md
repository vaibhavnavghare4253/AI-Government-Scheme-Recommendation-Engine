# Deployment Guide

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Terraform >= 1.0
- Docker
- kubectl (for EKS deployment)

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd scheme-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your local configuration
# DATABASE_URL, AWS credentials, etc.
```

### 3. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 4. Run Migrations
```bash
# Enter backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head
```

### 5. Access Application
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:3000

## AWS Production Deployment

### Phase 1: Infrastructure Setup

#### 1. Create S3 Bucket for Terraform State
```bash
aws s3 mb s3://scheme-platform-terraform-state --region ap-south-1
aws s3api put-bucket-versioning \
  --bucket scheme-platform-terraform-state \
  --versioning-configuration Status=Enabled
```

#### 2. Configure Terraform Variables
```bash
cd infrastructure/terraform

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
aws_region = "ap-south-1"
environment = "production"
vpc_cidr = "10.0.0.0/16"
availability_zones = ["ap-south-1a", "ap-south-1b"]

# Database
db_name = "schemes_db"
db_username = "admin"
db_password = "<secure-password>"
db_instance_class = "db.t3.medium"

# ECS
container_image = "<account-id>.dkr.ecr.ap-south-1.amazonaws.com/scheme-backend:latest"
ecs_desired_count = 2

# Domain
domain_name = "schemes.gov.in"
EOF
```

#### 3. Initialize and Apply Terraform
```bash
terraform init
terraform plan
terraform apply
```

This will create:
- VPC with public/private subnets across 2 AZs
- RDS PostgreSQL (Multi-AZ)
- ECS Cluster with Fargate
- Application Load Balancer
- S3 buckets for documents and assets
- Cognito User Pool
- CloudFront distribution
- Security groups and IAM roles

### Phase 2: Application Deployment

#### 1. Build and Push Docker Image
```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Build image
cd backend
docker build -t scheme-backend:latest .

# Tag and push
docker tag scheme-backend:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/scheme-backend:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/scheme-backend:latest
```

#### 2. Run Database Migrations
```bash
# Get RDS endpoint from Terraform output
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Run migrations via ECS task
aws ecs run-task \
  --cluster scheme-platform-prod \
  --task-definition scheme-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

#### 3. Deploy Frontend to S3
```bash
cd frontend

# Build production bundle
npm run build

# Sync to S3
aws s3 sync build/ s3://scheme-platform-assets-prod/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <distribution-id> \
  --paths "/*"
```

### Phase 3: Configure Services

#### 1. Setup Cognito
```bash
# Get Cognito User Pool ID
POOL_ID=$(terraform output -raw cognito_user_pool_id)

# Create admin user
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com \
  --temporary-password TempPass123!
```

#### 2. Configure Secrets
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name prod/scheme-platform/db \
  --secret-string '{"username":"admin","password":"<db-password>"}'

aws secretsmanager create-secret \
  --name prod/scheme-platform/jwt \
  --secret-string '{"secret":"<jwt-secret>"}'
```

#### 3. Setup CloudWatch Alarms
```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name scheme-platform-high-errors \
  --alarm-description "Alert when error rate exceeds 1%" \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name scheme-platform-high-latency \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 1.0 \
  --comparison-operator GreaterThanThreshold
```

### Phase 4: CI/CD Setup

#### 1. GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1
      
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/scheme-backend:$IMAGE_TAG backend/
          docker push $ECR_REGISTRY/scheme-backend:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster scheme-platform-prod \
            --service scheme-backend \
            --force-new-deployment
```

## Monitoring and Maintenance

### CloudWatch Dashboards

Create custom dashboard:
```bash
aws cloudwatch put-dashboard \
  --dashboard-name scheme-platform-prod \
  --dashboard-body file://cloudwatch-dashboard.json
```

### Log Aggregation

View logs:
```bash
# Backend logs
aws logs tail /ecs/scheme-backend --follow

# Filter errors
aws logs filter-log-events \
  --log-group-name /ecs/scheme-backend \
  --filter-pattern "ERROR"
```

### Database Backups

Automated backups are enabled by default. Manual snapshot:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier scheme-platform-prod \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d)
```

### Scaling

#### Manual Scaling
```bash
# Scale ECS service
aws ecs update-service \
  --cluster scheme-platform-prod \
  --service scheme-backend \
  --desired-count 5
```

#### Auto-scaling (already configured in Terraform)
- CPU > 70%: Scale out
- CPU < 30%: Scale in
- Min: 2 tasks
- Max: 50 tasks

## Rollback Procedure

### 1. Rollback ECS Deployment
```bash
# List task definitions
aws ecs list-task-definitions --family-prefix scheme-backend

# Update to previous version
aws ecs update-service \
  --cluster scheme-platform-prod \
  --service scheme-backend \
  --task-definition scheme-backend:PREVIOUS_VERSION
```

### 2. Rollback Database Migration
```bash
# Connect to RDS
psql -h $RDS_ENDPOINT -U admin -d schemes_db

# Run Alembic downgrade
alembic downgrade -1
```

### 3. Rollback Frontend
```bash
# Restore previous S3 version
aws s3api list-object-versions \
  --bucket scheme-platform-assets-prod \
  --prefix index.html

aws s3api copy-object \
  --bucket scheme-platform-assets-prod \
  --copy-source scheme-platform-assets-prod/index.html?versionId=PREVIOUS_VERSION \
  --key index.html
```

## Security Checklist

- [ ] Enable AWS WAF on ALB and CloudFront
- [ ] Configure AWS Shield for DDoS protection
- [ ] Enable VPC Flow Logs
- [ ] Enable CloudTrail for audit logging
- [ ] Rotate database credentials regularly
- [ ] Enable MFA for admin accounts
- [ ] Configure Security Groups with least privilege
- [ ] Enable encryption at rest for all data stores
- [ ] Use HTTPS only (enforce via CloudFront)
- [ ] Regular security scanning with AWS Inspector

## Cost Optimization

1. Use Reserved Instances for predictable workloads
2. Enable S3 Intelligent-Tiering
3. Use CloudFront caching aggressively
4. Archive old logs to S3 Glacier
5. Right-size RDS instances based on metrics
6. Use Spot Instances for non-critical tasks

## Troubleshooting

### Service Not Starting
```bash
# Check ECS task logs
aws ecs describe-tasks \
  --cluster scheme-platform-prod \
  --tasks <task-id>

# Check CloudWatch logs
aws logs tail /ecs/scheme-backend --follow
```

### Database Connection Issues
```bash
# Test connectivity from ECS task
aws ecs execute-command \
  --cluster scheme-platform-prod \
  --task <task-id> \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside container
nc -zv $RDS_ENDPOINT 5432
```

### High Latency
```bash
# Check RDS performance
aws rds describe-db-instances \
  --db-instance-identifier scheme-platform-prod

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=scheme-platform-prod \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## Support

For issues or questions:
- Technical: tech-support@schemes.gov.in
- Infrastructure: devops@schemes.gov.in
- Security: security@schemes.gov.in
