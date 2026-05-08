module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.app_name}-vpc"
  cidr = "10.0.0.0/16"

  azs            = ["us-east-1a", "us-east-1b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  # ── No private subnets, no NAT ────────────────────────────────────────────
  private_subnets    = []
  enable_nat_gateway = false    # ← No NAT gateway
  single_nat_gateway = false

  map_public_ip_on_launch = true  # ← Assign public IP to resources
  enable_dns_hostnames    = true
  enable_dns_support      = true

  tags = {
    App         = var.app_name
    Environment = var.environment
  }
}