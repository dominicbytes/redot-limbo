param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string[]] $Library
)

$ErrorActionPreference = "Stop"
$visualStudioRoots = @(
    "$env:ProgramFiles\Microsoft Visual Studio\2022",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022"
) | Where-Object { Test-Path -LiteralPath $_ }
$dumpbin = Get-ChildItem -Path $visualStudioRoots -Recurse -Filter "dumpbin.exe" |
    Where-Object { $_.FullName -like "*\bin\Hostx64\x64\dumpbin.exe" } |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if ($null -eq $dumpbin) {
    throw "Visual Studio x64 dumpbin.exe was not found."
}

$forbiddenPatterns = @(
    "D:\Claude Vault",
    "/workspace",
    "LIMBOAI_FIXTURE",
    "ghp_",
    "BEGIN RSA PRIVATE",
    "BEGIN OPENSSH PRIVATE",
    "BEGIN EC PRIVATE"
)

foreach ($path in $Library) {
    $resolved = (Resolve-Path -LiteralPath $path).Path
    $dump = & $dumpbin.FullName /headers /dependents /exports $resolved | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "dumpbin failed for $resolved"
    }
    if ($dump -notmatch "8664 machine \(x64\)") {
        throw "Not an x64 PE library: $resolved"
    }
    if ($dump -notmatch "\blimboai_init\b") {
        throw "limboai_init is not exported by $resolved"
    }
    if ($dump -notmatch "KERNEL32\.dll") {
        throw "Expected KERNEL32.dll dependency is missing from $resolved"
    }
    if ($dump -match "(?i)VCRUNTIME|MSVCP|ucrtbase") {
        throw "Unexpected dynamic C/C++ runtime dependency in $resolved"
    }

    $binaryText = [System.Text.Encoding]::GetEncoding(28591).GetString(
        [System.IO.File]::ReadAllBytes($resolved)
    )
    foreach ($pattern in $forbiddenPatterns) {
        if ($binaryText.Contains($pattern)) {
            throw "Forbidden embedded string '$pattern' found in $resolved"
        }
    }

    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $resolved
    $signature = Get-AuthenticodeSignature -LiteralPath $resolved
    [PSCustomObject]@{
        Path = $resolved
        Bytes = (Get-Item -LiteralPath $resolved).Length
        SHA256 = $hash.Hash
        Machine = "x86_64"
        Dependencies = "KERNEL32.dll"
        Export = "limboai_init"
        Signature = $signature.Status
        ForbiddenStrings = 0
    }
}
