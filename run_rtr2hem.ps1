# https://github.com/astral-sh/uv/releases
$env:UV_INSTALL = ".\uv\uv-x86_64-pc-windows-msvc.zip"

$env:US_INSTALL_DIR = ".\uv"
$env:UV_PYTHON_INSTALL_DIR = ".\.python"
$env:UV_CACHE_DIR = ".\.uv_cache"

# not already on the path
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    # not already unzipped
    if (-not (Test-Path ".\uv\uv.exe")) {
        Expand-Archive -Path $env:UV_INSTALL -DestinationPath $env:US_INSTALL_DIR 
    }
    New-Alias -Name uv -Value .\uv\uv.exe -ErrorAction SilentlyContinue
}

uv run .\main.py
