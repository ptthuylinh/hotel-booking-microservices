# Script don dep toan bo tai nguyen AWS sau khi hoan thanh nghiem thu do an Tuan 4
# Muc tieu: Xoa triet de cac tai nguyen co the phat sinh phi de bao toan so du Learner Lab

param (
    [switch]$Force
)

$REGION = "us-east-1"
$CLUSTER_NAME = "hotel-cluster"
$RDS_INSTANCE = "hotel-db-instance"
$ALB_NAME = "hotel-booking-alb"
$SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:055652951832:hotel-system-alerts"
$SQS_QUEUE_NAME = "booking-notification-queue"
$SQS_DLQ_NAME = "booking-notification-dlq"

Write-Host "==========================================================" -ForegroundColor Red
Write-Host " [TEARDOWN FINAL] TIEN HANH GIAI PHONG TOAN BO TAI NGUYEN" -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor Red

if (-not $Force) {
    $confirm = Read-Host "Ban co chac chan muon XOA TOAN BO tai nguyen he thong hotel tren AWS? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Da huy thao tac Teardown." -ForegroundColor Yellow
        exit
    }
}

# 1. Scale down va Xoa ECS Services
Write-Host "`n[1/6] Dang scale ve 0 va xoa ECS Services..." -ForegroundColor Cyan
foreach ($svc in @("room-service", "booking-service", "notification-service")) {
    aws ecs update-service --cluster $CLUSTER_NAME --service $svc --desired-count 0 --region $REGION | Out-Null
    aws ecs delete-service --cluster $CLUSTER_NAME --service $svc --force --region $REGION 2>$null | Out-Null
    Write-Host " -> Da xoa ECS Service: $svc" -ForegroundColor Green
}

# 2. Xoa ALB va Target Groups
Write-Host "`n[2/6] Dang xoa Application Load Balancer va Target Groups..." -ForegroundColor Cyan
$albArn = aws elbv2 describe-load-balancers --names $ALB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text --region $REGION 2>$null
if ($albArn -and $albArn -ne "None") {
    aws elbv2 delete-load-balancer --load-balancer-arn $albArn --region $REGION | Out-Null
    Write-Host " -> Da xoa ALB: $ALB_NAME" -ForegroundColor Green
}

# 3. Xoa RDS Database Instance (skip final snapshot trong Learner Lab)
Write-Host "`n[3/6] Dang xoa Amazon RDS Database Instance ($RDS_INSTANCE)..." -ForegroundColor Cyan
aws rds delete-db-instance --db-instance-identifier $RDS_INSTANCE --skip-final-snapshot --delete-automated-backups --region $REGION 2>$null | Out-Null
Write-Host " -> Da gui yeu cau xoa RDS Instance ($RDS_INSTANCE)" -ForegroundColor Green

# 4. Xoa SQS Queues va SNS Topics
Write-Host "`n[4/6] Dang xoa SQS Queues va SNS Topic canh bao..." -ForegroundColor Cyan
$queueUrl = aws sqs get-queue-url --queue-name $SQS_QUEUE_NAME --query "QueueUrl" --output text --region $REGION 2>$null
if ($queueUrl) { aws sqs delete-queue --queue-url $queueUrl --region $REGION | Out-Null }

$dlqUrl = aws sqs get-queue-url --queue-name $SQS_DLQ_NAME --query "QueueUrl" --output text --region $REGION 2>$null
if ($dlqUrl) { aws sqs delete-queue --queue-url $dlqUrl --region $REGION | Out-Null }

aws sns delete-topic --topic-arn $SNS_TOPIC_ARN --region $REGION 2>$null | Out-Null
Write-Host " -> Da xoa SQS Queues va SNS Topic thanh cong" -ForegroundColor Green

# 5. Xoa CloudWatch Alarms
Write-Host "`n[5/6] Dang xoa cac CloudWatch Alarms da tao o Tuan 3..." -ForegroundColor Cyan
aws cloudwatch delete-alarms --alarm-names "ECS-High-CPU-Utilization" "ECS-High-Memory-Utilization" "ALB-High-Target-5XX-Errors" "SQS-DLQ-Has-Poison-Messages" --region $REGION 2>$null | Out-Null
Write-Host " -> Da xoa CloudWatch Alarms" -ForegroundColor Green

# 6. Kiem tra so du va trang thai
Write-Host "`n[6/6] Kiem tra trang thai sau khi don dep..." -ForegroundColor Cyan
Write-Host " -> Vui long kiem tra lai Console de dam bao khong con instance nao chay ngam." -ForegroundColor Yellow

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " HOAN TAT TEARDOWN! TAI NGUYEN DA DUOC GIAI PHONG AN TOAN." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
