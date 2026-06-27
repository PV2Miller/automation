<#
.SYNOPSIS
    CRMiller Portfolio Intelligence Control Script - Status Object Parser
.DESCRIPTION
    Executes the Python macro engine, captures status payloads, 
    and writes metrics directly to disk.
#>
$TargetDir = "C:\automation"
$EngineScript = "$TargetDir\macro_analysis.py"
$LogFile = "$TargetDir\portfolio_digest_history.log"

Write-Output "=== PORTFOLIO INTELLIGENCE PIPELINE INITIALIZED ==="

if (-not (Test-Path $EngineScript)) {
    Write-Error "Execution aborted: Mathematical engine missing at $EngineScript"
    exit 1
}

Write-Output "Running Python Macro Intelligence Engine..."
$RawJson = python $EngineScript 2>$null

try {
    $Digest = $RawJson | ConvertFrom-Json -ErrorAction Stop
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Output "Execution successful."
    Write-Output "Timestamp: $Timestamp"
    Write-Output "-----------------------------------------------"
    
    # Clean output generation based on what Python returns
    [PSCustomObject]@{
        RunStatus = if ($null -ne $Digest.status) { $Digest.status } else { "UNKNOWN" }
        Processed = if ($null -ne $Digest.processed) { $Digest.processed } else { 0 }
    } | Format-List

    # Log generation
    $LogPayload = @{
        Timestamp = $Timestamp
        Payload   = $Digest
    } | ConvertTo-Json -Depth 3
    
    $LogPayload | Out-File -FilePath $LogFile -Append -Encoding utf8
    Write-Output "Telemetry log updated safely at: $LogFile"

} catch {
    Write-Error "Pipeline Fault: Failed to parse engine output stream. Raw data was not valid JSON."
}
