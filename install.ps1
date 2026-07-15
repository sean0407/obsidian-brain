# obsidian-brain installer for Windows PowerShell
# Usage: irm https://raw.githubusercontent.com/sean0407/obsidian-brain/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  obsidian-brain installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Clone or update
$InstallDir = Join-Path $HOME "obsidian-brain"

if (Test-Path $InstallDir) {
    Write-Host "Existing installation found. Updating..." -ForegroundColor Yellow
    Set-Location $InstallDir
    git pull
} else {
    Write-Host "Cloning obsidian-brain to $InstallDir..." -ForegroundColor Green
    git clone https://github.com/sean0407/obsidian-brain.git $InstallDir
    Set-Location $InstallDir
}

# Install Python deps
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install python-frontmatter pyyaml -q

# Prompt for vault path
Write-Host ""
$VaultPath = Read-Host "Enter your Obsidian vault path (e.g. C:\Users\YourName\OneDrive\_Obsidian)"

# Update config
$ConfigPath = Join-Path $InstallDir "config.yaml"
$Config = Get-Content $ConfigPath -Raw
$Config = $Config -replace 'vault_path:.*', "vault_path: `"$VaultPath`""
$Config | Set-Content $ConfigPath -Encoding UTF8

Write-Host ""
Write-Host "Configuration saved." -ForegroundColor Green

# Run init + audit
Write-Host ""
Write-Host "Initializing Karpathy wiki structure..." -ForegroundColor Green
python cli.py init

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installation complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open your Obsidian vault"
Write-Host "  2. Edit CLAUDE.md to customize your schema"
Write-Host "  3. Run 'python cli.py audit' any time to check compliance"
Write-Host ""
