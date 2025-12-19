# Clear Python cache and run the game
Write-Host "Clearing Python cache..." -ForegroundColor Yellow

# Remove __pycache__ directories
Get-ChildItem -Path "." -Name "__pycache__" -Recurse -Directory -Force | ForEach-Object {
    Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
}

# Remove .pyc files
Get-ChildItem -Path "." -Name "*.pyc" -Recurse -Force | ForEach-Object {
    Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue
}

# Remove .pytest_cache
Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cache cleared!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Snake Adaptive AI..." -ForegroundColor Cyan
Write-Host ""

python src/game_demo.py
