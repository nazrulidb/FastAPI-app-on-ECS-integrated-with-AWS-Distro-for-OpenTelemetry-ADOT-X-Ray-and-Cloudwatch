# ── CloudWatch Log Groups ─────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "fastapi" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "adot" {
  name              = "/ecs/${var.app_name}-adot"
  retention_in_days = 30
}

# ── ECS Cluster ───────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"
}

# ── ECS Task Definition ───────────────────────────────────────────────────────
resource "aws_ecs_task_definition" "main" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    # ── Container 1: FastAPI App ───────────────────────────────────────────
    {
      name      = var.app_name
      image     = var.docker_image
      essential = true

      portMappings = [{
        containerPort = var.container_port
        protocol      = "tcp"
      }]

      environment = [
        {
          name  = "DATABASE_URL"
          value = var.database_url
        },
        {
          name  = "OTEL_SERVICE_NAME"
          value = var.app_name
        },
        {
          name  = "OTEL_EXPORTER_OTLP_ENDPOINT"
          value = "http://localhost:4317"
        },
        {
          name  = "OTEL_PROPAGATORS"
          value = "xray,tracecontext"
        },
        {
          name  = "OTEL_PYTHON_DISTRO"
          value = "aws_distro"
        },
        {
          name  = "OTEL_PYTHON_CONFIGURATOR"
          value = "aws_configurator"
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "OTEL_EXPORTER_OTLP_PROTOCOL"
          value = "grpc" # Force gRPC for port 4317
        },
        {
          name  = "OTEL_TRACES_SAMPLER"
          value = "always_on" # Force 100% sampling for debugging
        },
        {
          name  = "OTEL_RESOURCE_ATTRIBUTES"
          value = "service.name=${var.app_name},deployment.environment=${var.environment}"
        }
      ]

      dependsOn = [{
        containerName = "adot-collector"
        condition     = "START"
      }]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fastapi.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "fastapi"
        }
      }
    },

    # ── Container 2: ADOT Collector ───────────────────────────────────────
    {
      name      = "adot-collector"
      image     = "public.ecr.aws/aws-observability/aws-otel-collector:latest"
      essential = false

      
      portMappings = [
        { containerPort = 4317, protocol = "tcp" },
        { containerPort = 4318, protocol = "tcp" }
      ]
      environment = [
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
       ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.adot.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "adot"
        }
      }
    }
  ])
}

# ── ECS Service ───────────────────────────────────────────────────────────────
resource "aws_ecs_service" "main" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true   # private subnet — behind ALB
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.main]
}
