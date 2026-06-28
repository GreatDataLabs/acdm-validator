# CI/CD usage

## GitHub Actions

```yaml
- uses: actions/setup-python@v5
  with: {python-version: "3.12"}
- run: pip install acdm-validator
- run: acdm-validate contracts/ --format json --output acdm-report.json
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: acdm-report
    path: acdm-report.json
```

## Azure DevOps

```yaml
- task: UsePythonVersion@0
  inputs: {versionSpec: "3.12"}
- script: pip install acdm-validator
- script: acdm-validate contracts/ --format json --output $(Build.ArtifactStagingDirectory)/acdm-report.json
- publish: $(Build.ArtifactStagingDirectory)/acdm-report.json
  artifact: acdm-report
  condition: always()
```

Use `--fail-on L1`, `L2`, or `L3` while progressively adopting deeper checks. The standard `error`
policy enables every implemented rule.

