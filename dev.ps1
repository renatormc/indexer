try {
    Push-Location "D:\gdrive\Documentos" #removeline
    uv run --project "$PSScriptRoot" "$PSScriptRoot\main.py" $args
}
finally {
    Pop-Location
}