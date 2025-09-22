$ErrorActionPreference = "Stop"
$python = ".\.venv_x64\Scripts\python.exe"

& $python manage.py check --deploy; if ($LASTEXITCODE) { throw "check --deploy failed" }
& $python manage.py migrate --check; if ($LASTEXITCODE) { throw "migrate --check failed" }
& $python manage.py collectstatic --noinput; if ($LASTEXITCODE) { throw "collectstatic failed" }
& $python manage.py spectacular --file api-schema.yaml; if ($LASTEXITCODE) { throw "spectacular failed" }

Write-Host "Smoke test prod-like OK" -ForegroundColor Green
