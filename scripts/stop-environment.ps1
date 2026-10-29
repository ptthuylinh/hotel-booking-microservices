# Script dung toan bo tai nguyen vao cuoi buoi thuc hanh de tiet kiem chi phi Lab
# Tac vu: Scale ECS Services ve 0 va Tam dung (Stop) Amazon RDS Instance

$REGION = "us-east-1"
$CLUSTER_NAME = "hotel-cluster"
$RDS_INSTANCE = "hotel-db-instance"

Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " [STOP LAB] DANG TIEN HANH HA TAI TOAN BO HE THONG HOTEL" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow

# 1. Scale down ECS Services
Write-Host "`n[1/2] Dang scale ca 3 ECS Services ve 0 task..." -ForegroundColor Cyan
aws ecs update-service --cluster $CLUSTER_NAME --service room-service --desired-count 0 --region $REGION | Out-Null
aws ecs update-service --cluster $CLUSTER_NAME --service booking-service --desired-count 0 --region $REGION | Out-Null
aws ecs update-service --cluster $CLUSTER_NAME --service notification-service --desired-count 0 --region $REGION | Out-Null
Write-Host " -> Da gui yeu cau scale 3 services ve 0 thanh cong!" -ForegroundColor Green

# 2. Stop RDS Instance
Write-Host "`n[2/2] Dang gui lenh Stop Amazon RDS Instance ($RDS_INSTANCE)..." -ForegroundColor Cyan
aws rds stop-db-instance --db-instance-identifier $RDS_INSTANCE --region $REGION | Out-Null
Write-Host " -> Da gui lenh stop RDS thanh cong!" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " DA DUNG HE THONG THANH CONG. NGAN SACH LAB DUOC AN TOAN!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
