Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$process = Get-Process Spotify -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 } |
    Select-Object -First 1

if ($null -eq $process) {
    Write-Host "Spotify main window not found."
    exit
}

$window = [System.Windows.Automation.AutomationElement]::FromHandle(
    [IntPtr]$process.MainWindowHandle
)

if ($null -eq $window) {
    Write-Host "Could not access Spotify's UI."
    exit
}

Write-Host "Spotify window found: $($process.MainWindowTitle)"

$elements = $window.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition
)

Write-Host "`n--- Current playback information ---"

$elements | ForEach-Object {
    $name = $_.Current.Name

    if (
        $name -like "Now playing:*" -or
        $name -match "advertisement|sponsored|^Ad$"
    ) {
        Write-Host $name
    }
}

Write-Host "`n--- Advertisement keyword scan ---"

$matches = @(
    $elements | Where-Object {
        $_.Current.Name -match "advertisement|sponsored|^Ad$"
    }
)

if ($matches.Count -eq 0) {
    Write-Host "No obvious advertisement labels found."
} else {
    $matches | ForEach-Object {
        Write-Host $_.Current.Name
    }
}