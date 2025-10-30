# 🚀 TestForge GitHub Actions - Quick Reference

## ⚡ Quick Commands

### **Run Full Integration Test**
```bash
gh workflow run api-integration-test.yml -f testName=my-test
```

### **Run Individual Actions**
```bash
# 1. Download example template
gh workflow run action-1-download-example.yml

# 2. Generate combinations
gh workflow run action-2-combination.yml -f inputFile=data/input.xlsx

# 3. Compile tests
gh workflow run action-3-compile.yml -f testName=suite -f inputFile=data/filled.xlsx

# 4. Run tests
gh workflow run action-4-run-stream.yml -f testName=suite

# 5. Download report
gh workflow run action-5-download-report.yml -f testName=suite
```

---

## 📊 Monitor Workflows

```bash
# List recent runs
gh run list --workflow=api-integration-test.yml

# Watch live
gh run watch

# View specific run
gh run view <RUN_ID>

# Download artifacts
gh run download <RUN_ID>
```

---

## 🔧 Common Inputs

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `testName` | Test suite name | `github-action-test` | `staging-smoke` |
| `inputFile` | Path to input file | uses example | `data/tests.xlsx` |
| `timestamp` | Report timestamp | latest | `20251030_143022` |

---

## 📦 Artifacts

| Workflow | Artifact Name | Retention |
|----------|---------------|-----------|
| Integration Test | `testforge-reports-{testName}` | 30 days |
| Download Example | `example-template` | 7 days |
| Generate Combos | `test-combinations` | 14 days |
| Compile Tests | `compiled-tests-{testName}` | 30 days |
| Run Stream | `test-stream-output-{testName}` | 14 days |
| Download Report | `test-report-{testName}` | 30 days |

---

## 🐛 Troubleshooting

### **Check Server Logs**
```bash
# Download artifacts and check server.log
gh run download <RUN_ID>
cat testforge-reports-*/server.log
```

### **Check SSE Output**
```bash
# View streaming test execution
cat testforge-reports-*/sse_output.log
```

### **Re-run Failed Workflow**
```bash
gh run rerun <RUN_ID>
```

---

## 🎯 Best Practices

✅ Use descriptive `testName` values (e.g., `api-smoke-test`, `regression-suite`)  
✅ Store input files in `data/` directory  
✅ Download artifacts immediately after run completion  
✅ Review `compile_response.json` for compilation details  
✅ Check `sse_output.log` for test execution progress  
✅ Use timestamp parameter for specific report downloads  

---

**Full Documentation:** [.github/workflows/README.md](.github/workflows/README.md)
