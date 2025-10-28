# Inicia Ollama (si ya está corriendo, esto no molesta)
Start-Process -WindowStyle Minimized -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "serve"
Start-Sleep -Seconds 3
# Inicia FastAPI
uvicorn app:app --host 0.0.0.0 --port 8000 --reload