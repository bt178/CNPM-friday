# Test CollabSphere Backend Endpoints

Write-Host "Testing CollabSphere Backend Endpoints..." -ForegroundColor Cyan
Write-Host ""

# Test root endpoint
Write-Host "1. Testing root endpoint (GET /):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test health endpoint
Write-Host "2. Testing health endpoint (GET /health):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test docs endpoint
Write-Host "3. API Documentation available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   (Open this URL in your browser)" -ForegroundColor Cyan

