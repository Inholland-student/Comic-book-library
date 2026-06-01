function Get-TfvarsValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    if (!(Test-Path $FilePath)) {
        throw "tfvars file not found: $FilePath"
    }

    $content = Get-Content $FilePath -ErrorAction Stop
    foreach ($line in $content) {
        if ($line -match "^\s*$Key\s*=\s*`"([^`"]+)`"") {
            return $Matches[1]
        }
    }

    throw "Key '$Key' not found in $FilePath"
}

function Get-RequiredCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $Command = Get-Command $Name -ErrorAction SilentlyContinue

    if ($Command) {
        return $Command.Source
    }

    $PossiblePaths = @(
        "C:\ProgramData\chocolatey\bin\$Name.exe",
        "$env:USERPROFILE\scoop\shims\$Name.exe",
        "$env:ProgramFiles\$Name\$Name.exe"
    )

    foreach ($Path in $PossiblePaths) {
        if (Test-Path $Path) {
            return $Path
        }
    }

    throw "$Name was not found. Install it or add it to PATH."
}