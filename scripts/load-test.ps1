# Script ban tai that vao Application Load Balancer de kiem thu hieu nang & kich hoat ECS Auto Scaling
# Yeu cau GVHD: "chay tai that va ghi ket qua thay doi so task, khong chi demo thu cong"

param (
    [Parameter(Mandatory=$false)]
    [string]$ALB_DNS = "http://hotel-booking-alb-xxxxxxxxxx.us-east-1.elb.amazonaws.com",

    [Parameter(Mandatory=$false)]
    [int]$TotalRequests = 200,

    [Parameter(Mandatory=$false)]
    [int]$Concurrency = 10
)

Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " [LOAD TESTING] BAT DAU CHAY TAI THAT VAO HE THONG ALB" -ForegroundColor Yellow
Write-Host " Endpoint ALB: $ALB_DNS" -ForegroundColor Cyan
Write-Host " Tong so requests: $TotalRequests | Do dong thoi: $Concurrency" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Yellow

$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$SuccessCount = 0
$FailCount = 0

Write-Host "`nDang gui $TotalRequests requests dong thoi vao API GET /api/rooms..." -ForegroundColor Yellow

$results = 1..$TotalRequests | ForEach-Object -Parallel {
    $alb = $using:ALB_DNS
    $reqIndex = $_
    $corrId = "loadtest-" + [System.Guid]::NewGuid().ToString()

    try {
        $startTime = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "$alb/api/rooms" -Method Get -Headers @{ "X-Correlation-Id" = $corrId } -TimeoutSec 10 -UseBasicParsing
        $startTime.Stop()
        [PSCustomObject]@{
            Index = $reqIndex
            StatusCode = $response.StatusCode
            DurationMs = $startTime.ElapsedMilliseconds
            Success = $true
        }
    } catch {
        [PSCustomObject]@{
            Index = $reqIndex
            StatusCode = $_.Exception.Response.StatusCode.value__
            DurationMs = 0
            Success = $false
        }
    }
} -ThrottleLimit $Concurrency

$Stopwatch.Stop()

$successList = $results | Where-Object { $_.Success -eq $true }
$failList = $results | Where-Object { $_.Success -eq $false }
$avgLatency = if ($successList.Count -gt 0) { ($successList | Measure-Object -Property DurationMs -Average).Average } else { 0 }

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " KET QUA KIEM THU TAI THAT (LOAD TEST SUMMARY):" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Tong thoi gian chay: $([math]::Round($Stopwatch.Elapsed.TotalSeconds, 2)) giay" -ForegroundColor Cyan
Write-Host " So request thanh cong (200 OK): $($successList.Count) / $TotalRequests" -ForegroundColor Green
Write-Host " So request that bai: $($failList.Count)" -ForegroundColor $(if ($failList.Count -gt 0) { "Red" } else { "Green" })
Write-Host " Do tre trung binh (Average Latency): $([math]::Round($avgLatency, 2)) ms" -ForegroundColor Cyan
Write-Host " Throughput uoc tinh: $([math]::Round($TotalRequests / $Stopwatch.Elapsed.TotalSeconds, 2)) requests/sec" -ForegroundColor Cyan
Write-Host "`n-> Quan sat tren CloudWatch Dashboard & ECS Console xem so Task da tu dong scale chua!" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
