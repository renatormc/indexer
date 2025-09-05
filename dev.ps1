try {
    Push-Location "D:\gdrive\Documentos\rindex"
    uv run --project "$PSScriptRoot" "$PSScriptRoot\main.py" $args
}
finally {
    Pop-Location
}