# Script khoi dong toan bo tai nguyen vao dau buoi thuc hanh
# Tac vu: Khoi dong RDS Instance -> Cho san sang -> Scale 3 ECS Services len 1 task

$REGION = "us-east-1"
$CLUSTER_NAME = "hotel-cluster"
$RDS_INSTANCE = "hotel-db-instance"

Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " [START LAB] DANG KHOI DONG HE THONG HOTEL MICROSERVICES" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow

# 1. Start RDS
Write-Host "`n[1/3] Dang khoi dong Amazon RDS Instance ($RDS_INSTANCE)..." -ForegroundColor Cyan
aws rds start-db-instance --db-instance-identifier $RDS_INSTANCE --region $REGION | Out-Null
Write-Host " -> Da gui lenh start RDS thanh cong!" -ForegroundColor Green

# 2. Wait for RDS available
Write-Host "`n[2/3] Dang cho RDS san sang (trang thai available, khoang 2-3 phut)..." -ForegroundColor Cyan
aws rds wait db-instance-available --db-instance-identifier $RDS_INSTANCE --region $REGION
Write-Host " -> RDS da san sang ket noi!" -ForegroundColor Green

# 3. Scale up ECS Services
Write-Host "`n[3/3] Dang scale 3 ECS Services len desired-count = 1..." -ForegroundColor Cyan
aws ecs update-service --cluster $CLUSTER_NAME --service room-service --desired-count 1 --region $REGION | Out-Null
aws ecs update-service --cluster $CLUSTER_NAME --service booking-service --desired-count 1 --region $REGION | Out-Null
aws ecs update-service --cluster $CLUSTER_NAME --service notification-service --desired-count 1 --region $REGION | Out-Null
Write-Host " -> Da gui yeu cau scale 3 services len 1 task thanh cong!" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " HE THONG DA DUOC KHOI DONG TOAN BO VA SAN SANG LAM VIEC!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
