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