$url = "https://khkvqkbssngclojtxkuv.supabase.co/auth/v1/admin/users"
$key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtoa3Zxa2Jzc25nY2xvanR4a3V2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODAyMTgwOSwiZXhwIjoyMDkzNTk3ODA5fQ._kgSuOGrqQWgPQcrn0kl9pDWcWCPKyZVGfYyDQa3D0g"
$password = "000000"

$users = @(
    "hok6@hok2.com.tw", "hok3@hok2.com.tw", "hok7@hok1.com.tw",
    "hok11@hok3.com.tw", "hok4@hok2.com.tw", "hok8@hok2.com.tw",
    "hok5@hok2.com.tw", "hok9@hok3.com.tw", "hok15@hok6.com.tw",
    "hok2@hok2.com.tw", "hok13@hok6.com.tw", "hok12@hok6.com.tw",
    "hok14@hok6.com.tw", "hok10@hok3.com.tw", "hok16@hok6.com.tw",
    "hok17@hok6.com.tw", "hok18@hok6.com.tw", "hok1@hok2.com.tw",
    "hok2f@hok6.com.tw"
)

$headers = @{
    "apikey" = $key
    "Authorization" = "Bearer $key"
    "Content-Type" = "application/json"
}

foreach ($email in $users) {
    Write-Host "Creating user: $email..."
    $body = @{
        "email" = $email
        "password" = $password
        "email_confirm" = $true
    } | ConvertTo-Json

    try {
        Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        Write-Host "Success: $email"
    } catch {
        Write-Host "Failed: $email - $($_.Exception.Message)"
    }
}
