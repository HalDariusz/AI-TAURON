# =============================================================================
#  Ollama @ HAL  —  jeden klik = połączenie  (Windows / PowerShell)
# -----------------------------------------------------------------------------
#  Uruchomienie:
#     .\connect.ps1            -> otwiera tunel SSH i pokazuje jak używać
#     .\connect.ps1 chat       -> otwiera tunel i wchodzi w czat z Bielikiem
#     .\connect.ps1 stop       -> zamyka tunel
#     .\connect.ps1 status     -> pokazuje stan tunelu
#
#  Wymaga wbudowanego klienta OpenSSH (Windows 10/11 mają go domyślnie).
#  Dwuklik: użyj connect.bat (uruchamia ten skrypt z pominięciem ExecutionPolicy).
# =============================================================================
param([string]$Action = "connect")

$ErrorActionPreference = "Stop"

$RemoteHost   = "95.217.89.69"
$SshUser      = "llmtunnel"
$RemotePort   = 11434
$DefaultModel = "SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M"

$Dir        = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Key        = Join-Path $Dir "id_ed25519_ollama"
$PidFile    = Join-Path $Dir ".tunnel.pid"
$PortFile   = Join-Path $Dir ".tunnel.port"
$UiDir      = Join-Path $Dir "ui"
$UiPidFile  = Join-Path $Dir ".ui.pid"
$UiPortFile = Join-Path $Dir ".ui.port"

function Ok($m)  { Write-Host "OK  $m"   -ForegroundColor Green }
function Inf($m) { Write-Host "..  $m"   -ForegroundColor Cyan }
function Err($m) { Write-Host "!!  $m"   -ForegroundColor Red }

function Fix-KeyPerms {
    # OpenSSH na Windows odmawia użycia klucza z "za szerokimi" uprawnieniami.
    # Usuwamy dziedziczenie i zostawiamy odczyt tylko dla bieżącego użytkownika.
    if (Test-Path $Key) {
        cmd /c "icacls `"$Key`" /inheritance:r" | Out-Null
        cmd /c "icacls `"$Key`" /grant:r `"$($env:USERNAME):(R)`"" | Out-Null
    }
}

function Port-Busy($p) {
    try {
        $null = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction Stop
        return $true
    } catch { return $false }
}

function Kill-Strays {
    # ubij ewentualne osierocone tunele ssh do naszego hosta
    Get-CimInstance Win32_Process -Filter "Name='ssh.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*$SshUser@$RemoteHost*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}

function Stop-Ui {
    if (Test-Path $UiPidFile) {
        $uid = (Get-Content $UiPidFile | Select-Object -First 1) -as [int]
        if ($uid) { Stop-Process -Id $uid -Force -ErrorAction SilentlyContinue }
        Remove-Item $UiPidFile,$UiPortFile -ErrorAction SilentlyContinue
    }
}

function Open-Ui {
    $p = if (Test-Path $PortFile) { Get-Content $PortFile } else { $RemotePort }
    $py = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
    if (-not $py) {
        Err "Do interfejsu WWW potrzebny jest Python. Zainstaluj z https://www.python.org lub użyj czatu: .\connect.ps1 chat"
        return
    }
    if (-not (Test-Path (Join-Path $UiDir "chat.html"))) { Err "Brak pliku ui\chat.html"; return }

    $uiport = 8800
    while (Port-Busy $uiport) { $uiport++ }
    $proc = Start-Process $py -ArgumentList @("-m","http.server","$uiport","--bind","127.0.0.1") `
                -WorkingDirectory $UiDir -WindowStyle Hidden -PassThru
    $proc.Id | Out-File -Encoding ascii $UiPidFile
    $uiport  | Out-File -Encoding ascii $UiPortFile
    Start-Sleep -Seconds 1

    $url = "http://127.0.0.1:$uiport/chat.html?api=$p"
    Ok "Interfejs WWW: $url"
    Start-Process $url
}

function Tunnel-Alive {
    if (Test-Path $PidFile) {
        $procId = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1) -as [int]
        if ($procId -and (Get-Process -Id $procId -ErrorAction SilentlyContinue)) { return $true }
    }
    return $false
}

function Stop-Tunnel {
    if (Tunnel-Alive) {
        $procId = (Get-Content $PidFile | Select-Object -First 1) -as [int]
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Kill-Strays
        Stop-Ui
        Remove-Item $PidFile,$PortFile -ErrorAction SilentlyContinue
        Ok "Tunel zamknięty."
    } else {
        Kill-Strays
        Stop-Ui
        Inf "Tunel nie był uruchomiony."
        Remove-Item $PidFile,$PortFile -ErrorAction SilentlyContinue
    }
}

function Start-Tunnel {
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
        Err "Brak klienta 'ssh'. Zainstaluj OpenSSH Client (Ustawienia > Aplikacje > Funkcje opcjonalne)."
        exit 1
    }
    Fix-KeyPerms

    if (Tunnel-Alive) {
        $script:LocalPort = if (Test-Path $PortFile) { [int](Get-Content $PortFile) } else { $RemotePort }
        Inf "Tunel już działa (port $script:LocalPort) — używam istniejącego."
        return
    }

    # brak śladu w PID — posprzątaj ewentualne osierocone tunele
    Kill-Strays

    # znajdź wolny lokalny port (gdyby 11434 było zajęte przez własną Ollamę)
    $script:LocalPort = $RemotePort
    while (Port-Busy $script:LocalPort) { $script:LocalPort++ }

    Inf "Łączę z HAL ($RemoteHost) ..."
    $sshArgs = @(
        "-i", $Key,
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-N",
        "-L", "127.0.0.1:$($script:LocalPort):127.0.0.1:$RemotePort",
        "$SshUser@$RemoteHost"
    )
    $proc = Start-Process ssh -ArgumentList $sshArgs -WindowStyle Hidden -PassThru
    $proc.Id | Out-File -Encoding ascii $PidFile
    $script:LocalPort | Out-File -Encoding ascii $PortFile

    for ($i = 0; $i -lt 6; $i++) {
        Start-Sleep -Seconds 1
        try {
            Invoke-RestMethod -TimeoutSec 5 "http://127.0.0.1:$($script:LocalPort)/api/tags" | Out-Null
            Ok "Połączono. Ollama dostępna na  http://127.0.0.1:$($script:LocalPort)"
            return
        } catch { }
    }
    Err "Tunel otwarty, ale Ollama nie odpowiada. Spróbuj później lub napisz do Darka."
}

function Usage-Hint {
    $p = if (Test-Path $PortFile) { Get-Content $PortFile } else { $RemotePort }
    Write-Host ""
    Write-Host "  Jak używać:"
    if ("$p" -eq "11434") {
        Write-Host "    ollama run $DefaultModel"
    } else {
        Write-Host "    `$env:OLLAMA_HOST='127.0.0.1:$p'; ollama run $DefaultModel"
    }
    Write-Host "    Invoke-RestMethod http://127.0.0.1:$p/api/tags    # lista modeli"
    Write-Host ""
    Write-Host "  Rozłączenie:   .\connect.ps1 stop"
}

function Open-Chat {
    $p = if (Test-Path $PortFile) { Get-Content $PortFile } else { $RemotePort }
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Err "Nie znaleziono 'ollama'. Zainstaluj z https://ollama.com/download"
        Usage-Hint; return
    }
    Inf "Otwieram czat z Bielikiem (wyjście: /bye)"
    $env:OLLAMA_HOST = "127.0.0.1:$p"
    ollama run $DefaultModel
}

switch ($Action.ToLower()) {
    "stop"       { Stop-Tunnel }
    "disconnect" { Stop-Tunnel }
    "down"       { Stop-Tunnel }
    "status" {
        if (Tunnel-Alive) { Ok "Tunel działa (port $(Get-Content $PortFile), pid $(Get-Content $PidFile))" }
        else { Inf "Tunel nie działa." }
    }
    "chat"    { Start-Tunnel; Open-Chat }
    "ui"      { Start-Tunnel; Open-Ui }
    "web"     { Start-Tunnel; Open-Ui }
    "connect" { Start-Tunnel; Usage-Hint }
    default   { Write-Host "Użycie: .\connect.ps1 [connect|chat|ui|stop|status]" }
}
