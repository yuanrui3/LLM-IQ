# Save an API key from the clipboard into your Windows user environment, without printing it.
#   1. Click "Copy" next to the key on the provider's page (copy nothing else afterwards).
#   2. powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\save-key.ps1 DASHSCOPE_API_KEY
# New terminals see the variable automatically; iqaudit also reads it in terminals that were already open.
param([Parameter(Mandatory = $true)][string]$Name)

$c = Get-Clipboard -Raw
if ($c) { $c = $c.Trim() }

if ($c -match '^(sk-|AIza)\S{20,}$') {
    [Environment]::SetEnvironmentVariable($Name, $c, 'User')
    Write-Host "Saved $Name from the clipboard ($($c.Length) characters, starts with $($c.Substring(0, 6))...)."
} else {
    $len = if ($c) { $c.Length } else { 0 }
    Write-Host "The clipboard does not hold an API key (it holds $len characters)."
    Write-Host "Click Copy next to the key, copy nothing else, and run this again."
}
Remove-Variable c
