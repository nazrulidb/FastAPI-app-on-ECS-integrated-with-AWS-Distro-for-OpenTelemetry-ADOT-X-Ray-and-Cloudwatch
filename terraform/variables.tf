variable "aws_region" {
  default = "us-east-1"
}

variable "app_name" {
  default = "fastapi-hero"
}

variable "docker_image" {
  default = "nazrulidb/fastapi-hero:latest"
}

variable "container_port" {
  default = 8000
}

variable "cpu" {
  default = 512
}

variable "memory" {
  default = 1024
}

variable "desired_count" {
  default = 1
}

variable "database_url" {
  description = "Database URL"
  sensitive   = true
  default     = "sqlite+aiosqlite:///./heroes.db"
}

variable "environment" {
  default = "production"
}