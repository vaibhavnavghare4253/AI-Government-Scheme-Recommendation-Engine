terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "scheme-platform-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "ap-south-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Government Scheme Platform"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  azs         = var.availability_zones
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  instance_class      = var.db_instance_class
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"
  
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  container_image    = var.container_image
  container_port     = 8000
  desired_count      = var.ecs_desired_count
}

# S3 Buckets
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
}

# Cognito
module "cognito" {
  source = "./modules/cognito"
  
  environment = var.environment
}

# CloudFront
module "cloudfront" {
  source = "./modules/cloudfront"
  
  environment     = var.environment
  s3_bucket_id    = module.s3.assets_bucket_id
  alb_domain_name = module.ecs.alb_dns_name
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}

output "alb_dns_name" {
  value = module.ecs.alb_dns_name
}

output "cloudfront_domain" {
  value = module.cloudfront.domain_name
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}
