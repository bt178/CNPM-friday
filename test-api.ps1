# CollabSphere Backend - API Test Script
# Chạy: .\test-api.ps1

$baseUrl = "http://localhost:8000/api/v1"
$token = $null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    CollabSphere API Test Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n[TEST 1] Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Register Lecturer
Write-Host "`n[TEST 2] Register Lecturer..." -ForegroundColor Yellow
$lecturerEmail = "lecturer_$(Get-Random)@test.com"
$registerBody = @{
    email = $lecturerEmail
    password = "test123456"
    full_name = "Test Lecturer"
    role_id = 4
} | ConvertTo-Json

try {
    $user = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "✅ Registered: $($user.email)" -ForegroundColor Green
} catch {
    $error = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "⚠️ Register: $($error.detail)" -ForegroundColor Yellow
}

# Test 3: Login
Write-Host "`n[TEST 3] Login..." -ForegroundColor Yellow
$loginBody = "username=$lecturerEmail&password=test123456"
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $token = $loginResponse.access_token
    Write-Host "✅ Login successful! Token received." -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test 4: List Topics (without auth for students)
Write-Host "`n[TEST 4] List Topics..." -ForegroundColor Yellow
try {
    $topics = Invoke-RestMethod -Uri "$baseUrl/topics/" -Method GET -Headers $headers
    Write-Host "✅ Topics found: $($topics.total)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "⚠️ Topics: Status $statusCode (may need auth)" -ForegroundColor Yellow
}

# Test 5: Create Topic (Lecturer only)
Write-Host "`n[TEST 5] Create Topic..." -ForegroundColor Yellow
$topicBody = @{
    title = "Test Topic $(Get-Random)"
    description = "This is a test topic"
    objectives = "Testing objectives"
    tech_stack = "Python, FastAPI"
    dept_id = 1
} | ConvertTo-Json

try {
    $topic = Invoke-RestMethod -Uri "$baseUrl/topics/" -Method POST -Body $topicBody -ContentType "application/json" -Headers $headers
    Write-Host "✅ Topic created: $($topic.title) (ID: $($topic.topic_id))" -ForegroundColor Green
    $topicId = $topic.topic_id
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "❌ Create Topic failed ($statusCode): $($errorDetail.detail)" -ForegroundColor Red
}

# Test 6: List Projects
Write-Host "`n[TEST 6] List Projects..." -ForegroundColor Yellow
try {
    $projects = Invoke-RestMethod -Uri "$baseUrl/projects/" -Method GET -Headers $headers
    Write-Host "✅ Projects found: $($projects.Count)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "⚠️ Projects: Status $statusCode" -ForegroundColor Yellow
}

# Test 7: List Teams
Write-Host "`n[TEST 7] List Teams..." -ForegroundColor Yellow
try {
    $teams = Invoke-RestMethod -Uri "$baseUrl/teams/" -Method GET -Headers $headers
    Write-Host "✅ Teams found: $($teams.Count)" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "⚠️ Teams: Status $statusCode" -ForegroundColor Yellow
}

# Test 8: Test API Endpoint
Write-Host "`n[TEST 8] API Test Endpoint..." -ForegroundColor Yellow
try {
    $test = Invoke-RestMethod -Uri "$baseUrl/test" -Method GET
    Write-Host "✅ API: $($test.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Test endpoint failed" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "    Test Completed!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Open Swagger UI: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "2. Test more endpoints manually" -ForegroundColor Gray
Write-Host "3. Check Docker logs: docker logs collabsphere_backend" -ForegroundColor Gray
