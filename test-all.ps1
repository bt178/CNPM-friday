# CollabSphere API - Comprehensive Test Script
# Run: .\test-all.ps1

$baseUrl = "http://localhost:8000/api/v1"
$token = $null
$results = @()

function Write-TestResult {
    param($TestName, $Status, $Detail)
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }
    $icon = if ($Status -eq "PASS") { "[PASS]" } else { "[FAIL]" }
    Write-Host "$icon $TestName" -ForegroundColor $color
    if ($Detail) { Write-Host "       $Detail" -ForegroundColor Gray }
    $script:results += @{ Test = $TestName; Status = $Status; Detail = $Detail }
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      CollabSphere API - Comprehensive Test Suite       " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# ==========================================
# TEST GROUP 1: HEALTH
# ==========================================
Write-Host "--- TEST GROUP 1: Health ---" -ForegroundColor Yellow

# TC-001: Health Check
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    if ($health.status -eq "healthy") {
        Write-TestResult "TC-001: Health Check" "PASS" "Status: $($health.status)"
    }
}
catch {
    Write-TestResult "TC-001: Health Check" "FAIL" $_.Exception.Message
}

# TC-002: API Test Endpoint
try {
    $test = Invoke-RestMethod -Uri "$baseUrl/test" -Method GET
    Write-TestResult "TC-002: API Test Endpoint" "PASS" $test.message
}
catch {
    Write-TestResult "TC-002: API Test Endpoint" "FAIL" $_.Exception.Message
}

# ==========================================
# TEST GROUP 2: AUTHENTICATION
# ==========================================
Write-Host ""
Write-Host "--- TEST GROUP 2: Authentication ---" -ForegroundColor Yellow

$testEmail = "testuser_$(Get-Random)@collabsphere.com"

# TC-003: Register with role_name
try {
    $registerBody = @{
        email     = $testEmail
        password  = "SecurePass123"
        full_name = "Test User"
        role_name = "Lecturer"
    } | ConvertTo-Json
    
    $user = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    if ($user.role_name -eq "Lecturer" -and $user.role_id -eq 4) {
        Write-TestResult "TC-003: Register with role_name" "PASS" "User: $($user.email)"
    }
}
catch {
    Write-TestResult "TC-003: Register with role_name" "FAIL" $_.Exception.Message
}

# TC-004: Register Duplicate Email
try {
    $dup = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-TestResult "TC-004: Reject Duplicate Email" "FAIL" "Should have rejected"
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-TestResult "TC-004: Reject Duplicate Email" "PASS" "Correctly rejected"
    }
    else {
        Write-TestResult "TC-004: Reject Duplicate Email" "FAIL" $_.Exception.Message
    }
}

# TC-005: Login Valid
try {
    $loginBody = "username=" + $testEmail + "&password=SecurePass123"
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    if ($loginResponse.access_token) {
        $token = $loginResponse.access_token
        Write-TestResult "TC-005: Login Valid" "PASS" "Token received"
    }
}
catch {
    Write-TestResult "TC-005: Login Valid" "FAIL" $_.Exception.Message
}

# TC-006: Login Invalid Password
try {
    $badLogin = "username=" + $testEmail + "&password=wrongpassword"
    $resp = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $badLogin -ContentType "application/x-www-form-urlencoded"
    Write-TestResult "TC-006: Reject Wrong Password" "FAIL" "Should have rejected"
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-TestResult "TC-006: Reject Wrong Password" "PASS" "Correctly rejected"
    }
    else {
        Write-TestResult "TC-006: Reject Wrong Password" "FAIL" $_.Exception.Message
    }
}

$headers = @{ "Authorization" = "Bearer $token" }

# ==========================================
# TEST GROUP 3: TOPICS
# ==========================================
Write-Host ""
Write-Host "--- TEST GROUP 3: Topics (BE-PROJ-01) ---" -ForegroundColor Yellow

# TC-007: Create Topic
$topicId = $null
try {
    $topicBody = @{
        title       = "AI in Healthcare"
        description = "Research on AI applications"
        objectives  = "Develop ML models"
        tech_stack  = "Python, TensorFlow"
        dept_id     = 1
    } | ConvertTo-Json
    
    $topic = Invoke-RestMethod -Uri "$baseUrl/topics/" -Method POST -Body $topicBody -ContentType "application/json" -Headers $headers
    $topicId = $topic.topic_id
    Write-TestResult "TC-007: Create Topic" "PASS" "ID: $topicId, Status: $($topic.status)"
}
catch {
    Write-TestResult "TC-007: Create Topic" "FAIL" $_.Exception.Message
}

# TC-008: List Topics
try {
    $topics = Invoke-RestMethod -Uri "$baseUrl/topics/" -Method GET -Headers $headers
    Write-TestResult "TC-008: List Topics" "PASS" "Total: $($topics.total)"
}
catch {
    Write-TestResult "TC-008: List Topics" "FAIL" $_.Exception.Message
}

# TC-009: Get Topic by ID
try {
    $topicDetail = Invoke-RestMethod -Uri "$baseUrl/topics/$topicId" -Method GET -Headers $headers
    Write-TestResult "TC-009: Get Topic by ID" "PASS" "Title: $($topicDetail.title)"
}
catch {
    Write-TestResult "TC-009: Get Topic by ID" "FAIL" $_.Exception.Message
}

# TC-010: Submit Topic
try {
    $submitted = Invoke-RestMethod -Uri "$baseUrl/topics/$topicId/submit" -Method POST -Headers $headers
    if ($submitted.status -eq "pending") {
        Write-TestResult "TC-010: Submit Topic" "PASS" "Status: pending"
    }
}
catch {
    Write-TestResult "TC-010: Submit Topic" "FAIL" $_.Exception.Message
}

# ==========================================
# TEST GROUP 4: PROJECTS
# ==========================================
Write-Host ""
Write-Host "--- TEST GROUP 4: Projects (BE-PROJ-01) ---" -ForegroundColor Yellow

# TC-011: List Projects
try {
    $projects = Invoke-RestMethod -Uri "$baseUrl/projects/" -Method GET -Headers $headers
    Write-TestResult "TC-011: List Projects" "PASS" "Count: $($projects.Count)"
}
catch {
    Write-TestResult "TC-011: List Projects" "FAIL" $_.Exception.Message
}

# ==========================================
# TEST GROUP 5: TEAMS
# ==========================================
Write-Host ""
Write-Host "--- TEST GROUP 5: Teams (BE-TEAM-01) ---" -ForegroundColor Yellow

# TC-012: List Teams
try {
    $teams = Invoke-RestMethod -Uri "$baseUrl/teams/" -Method GET -Headers $headers
    Write-TestResult "TC-012: List Teams" "PASS" "Count: $($teams.Count)"
}
catch {
    Write-TestResult "TC-012: List Teams" "FAIL" $_.Exception.Message
}

# ==========================================
# SUMMARY
# ==========================================
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "                    TEST SUMMARY                        " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$total = $results.Count

Write-Host ""
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "  Passed:  $passed" -ForegroundColor Green
Write-Host "  Failed:  $failed" -ForegroundColor Red

if ($total -gt 0) {
    $passRate = [math]::Round(($passed / $total) * 100, 1)
    Write-Host ""
    Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Red" })
}

Write-Host ""
Write-Host "View Swagger UI: http://localhost:8000/docs" -ForegroundColor Gray
