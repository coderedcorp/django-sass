#!/usr/bin/env pwsh

<#
.SYNOPSIS
Compares code coverage percent of local coverage.xml file to main branch
(Azure Pipeline API).

.PARAMETER wd
The working directory in which to search for current coverage.xml.

.PARAMETER org
Name of the Azure DevOps organization where the pipeline is hosted.

.PARAMETER project
Name of the Azure DevOps project to which the pipeline belongs.

.PARAMETER pipeline_name
Name of the desired pipeline within the project. This is to support projects
with multiple pipelines.
#>


# ---- SETUP -------------------------------------------------------------------


param(
    [string] $wd = (Get-Item (Split-Path $PSCommandPath -Parent)).Parent,
    [string] $org = "coderedcorp",
    [string] $project = "cr-github",
    [string] $pipeline_name = "django-sass"
)

# Hide "UI" and progress bars.
$ProgressPreference = "SilentlyContinue"

# API setup.
$ApiBase = "https://dev.azure.com/$org/$project"


# ---- GET CODE COVERAGE FROM RECENT BUILD -------------------------------------


# Get list of all recent builds.
$mainBuildJson = (
    Invoke-WebRequest "$ApiBase/_apis/build/builds?branchName=refs/heads/main&api-version=5.1"
).Content | ConvertFrom-Json

# Get the latest matching build ID from the list of builds.
foreach ($build in $mainBuildJson.value) {
    if ($build.definition.name -eq $pipeline_name) {
        $mainLatestId = $build.id
        break
    }
}

# Retrieve code coverage for this build ID.
$mainCoverageJson = (
    Invoke-WebRequest "$ApiBase/_apis/test/codecoverage?buildId=$mainLatestId&api-version=5.1-preview.1"
).Content | ConvertFrom-Json
foreach ($cov in $mainCoverageJson.coverageData.coverageStats) {
    if ($cov.label -eq "Lines") {
        $mainlinerate = [math]::Round(($cov.covered / $cov.total) * 100, 2)
    }
}


# ---- GET COVERAGE FROM LOCAL RUN ---------------------------------------------


# Get current code coverage from coverage.xml file.
$coveragePath = Get-ChildItem -Recurse -Filter "coverage.xml" $wd
if (Test-Path -Path $coveragePath) {
    [xml]$BranchXML = Get-Content $coveragePath
}
else {
    Write-Host  -ForegroundColor Red `
        "No code coverage from this build. Is pytest configured to output code coverage? Exiting."
    exit 1
}
$branchlinerate = [math]::Round([decimal]$BranchXML.coverage.'line-rate' * 100, 2)


# ---- PRINT OUTPUT ------------------------------------------------------------


Write-Output ""
Write-Output "Main coverage rate:    $mainlinerate%"
Write-Output "Branch coverage rate:  $branchlinerate%"

if ($mainlinerate -eq 0) {
    $change = "Infinite"
}
else {
    $change = [math]::Abs($branchlinerate - $mainlinerate)
}

if ($branchlinerate -gt $mainlinerate) {
    Write-Host "Coverage increased by $change% 😀" -ForegroundColor Green
    exit 0
}
elseif ($branchlinerate -eq $mainlinerate) {
    Write-Host "Coverage has not changed." -ForegroundColor Green
    exit 0
}
else {
    Write-Host "Coverage decreased by $change% 😭" -ForegroundColor Red
    exit 4
}
