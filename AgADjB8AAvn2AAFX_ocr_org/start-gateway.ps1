$env:NOTION_TOKEN = [Environment]::GetEnvironmentVariable('NOTION_TOKEN','User')
$env:ORFREE_API_KEY = [Environment]::GetEnvironmentVariable('ORFREE_API_KEY','User')
$env:TELEGRAM_BOT_TOKEN = [Environment]::GetEnvironmentVariable('TELEGRAM_BOT_TOKEN','User')
$env:TINYFISH_API_KEY = [Environment]::GetEnvironmentVariable('TINYFISH_API_KEY','User')
$env:MISTRAL_API_KEY = [Environment]::GetEnvironmentVariable('MISTRAL_API_KEY','User')
$env:MISTRAL_API_KEY_2 = [Environment]::GetEnvironmentVariable('MISTRAL_API_KEY_2','User')
$env:MISTRAL_API_KEY_3 = [Environment]::GetEnvironmentVariable('MISTRAL_API_KEY_3','User')
$env:MISTRAL_OCR_MODEL = [Environment]::GetEnvironmentVariable('MISTRAL_OCR_MODEL','User')
$env:MISTRAL_ORGANIZE_MODEL = [Environment]::GetEnvironmentVariable('MISTRAL_ORGANIZE_MODEL','User')
# Load .env if present (overrides empty User vars)
$envFile = Join-Path $env:USERPROFILE '.nanobot\.env'
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    if ($_ -match '^\s*([^=]+)=(.*)$') {
      $k = $matches[1].Trim(); $v = $matches[2].Trim().Trim('"').Trim("'")
      if ($v -and -not [string]::IsNullOrWhiteSpace($v) -and -not $v.StartsWith('#')) {
        Set-Item -Path "env:$k" -Value $v
      }
    }
  }
}
& nanobot gateway

