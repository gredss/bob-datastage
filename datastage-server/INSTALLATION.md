# DataStage MCP Server - Installation Guide

## Prerequisites

Before installing the DataStage MCP Server, ensure you have:

1. **Node.js 18.x or higher** installed
2. **npm** (comes with Node.js)
3. **Cloud Pak for Data access** with DataStage
4. **CPD credentials** (API key or username/password)
5. **Bob IDE** installed

## Step 1: Verify Node.js Installation

Open PowerShell and check your Node.js version:

```powershell
node --version
# Should show v18.x.x or higher

npm --version
# Should show 9.x.x or higher
```

### If Node.js is Not Installed

Download and install from: https://nodejs.org/

Choose the LTS (Long Term Support) version.

## Step 2: Navigate to the Server Directory

```powershell
cd C:\Users\ArfanRusdi\AppData\Roaming\Bob-Code\MCP\datastage-server
```

## Step 3: Install Dependencies

```powershell
npm install
```

This will install all required packages:
- @modelcontextprotocol/sdk
- axios
- zod
- xml2js
- exceljs
- pdfkit
- chart.js
- canvas
- TypeScript and dev dependencies

**Note:** The `canvas` package may require additional build tools on Windows. If you encounter errors:

```powershell
# Install windows-build-tools (run as Administrator)
npm install --global windows-build-tools

# Then retry
npm install
```

## Step 4: Build the Server

```powershell
npm run build
```

This compiles TypeScript to JavaScript in the `build/` directory.

## Step 5: Get Your CPD Credentials

Follow the guide in `docs/cpd-authentication-guide.md` to obtain:

1. **CPD_URL**: Your Cloud Pak for Data cluster URL
   - Example: `https://cpd-instance.apps.cluster.techzone.ibm.com`

2. **CPD_API_KEY**: Your API key
   - Generate from CPD web interface → Profile → API key

3. **CPD_PROJECT_NAME**: Your DataStage project name
   - Example: `default_datastage_px`

## Step 6: Configure MCP Settings

Edit the Bob MCP settings file:

```powershell
notepad C:\Users\ArfanRusdi\.bob\settings\mcp_settings.json
```

Add the DataStage server configuration:

```json
{
  "mcpServers": {
    "datastage": {
      "command": "node",
      "args": [
        "C:\\Users\\ArfanRusdi\\AppData\\Roaming\\Bob-Code\\MCP\\datastage-server\\build\\index.js"
      ],
      "env": {
        "CPD_URL": "https://your-cpd-instance.apps.cluster.com",
        "CPD_API_KEY": "your-api-key-here",
        "CPD_PROJECT_NAME": "your-project-name",
        "CACHE_TTL": "300",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

**Important:** Replace the placeholder values with your actual credentials!

### Configuration Options

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CPD_URL` | Yes | CPD cluster URL | `https://cpd-ns.apps.cluster.com` |
| `CPD_API_KEY` | Yes* | API key for authentication | `eyJhbGc...` |
| `CPD_USERNAME` | Yes* | Username (if not using API key) | `admin` |
| `CPD_PASSWORD` | Yes* | Password (if not using API key) | `password123` |
| `CPD_PROJECT_NAME` | Yes | DataStage project name | `default_datastage_px` |
| `CACHE_TTL` | No | Cache duration in seconds | `300` (5 minutes) |
| `LOG_LEVEL` | No | Logging level | `info`, `debug`, `warn`, `error` |

*Either `CPD_API_KEY` OR `CPD_USERNAME`/`CPD_PASSWORD` is required.

## Step 7: Restart Bob IDE

Close and reopen Bob IDE to load the new MCP server.

## Step 8: Verify Installation

In Bob IDE, you should see the DataStage server listed under "Connected MCP Servers".

Try a test command:

```
Bob, list all DataStage jobs
```

Bob should respond with a list of jobs from your DataStage project.

## Troubleshooting

### Error: "Cannot find module"

**Solution:** Run `npm install` again to ensure all dependencies are installed.

### Error: "CPD_URL environment variable is required"

**Solution:** Check your MCP settings file. Ensure the `env` section has all required variables.

### Error: "Authentication failed"

**Solutions:**
1. Verify your API key is correct and hasn't expired
2. Check if your CPD URL is correct (no trailing slash)
3. Ensure your user has DataStage access permissions
4. Try regenerating your API key

### Error: "Project not found"

**Solutions:**
1. Verify the project name spelling (case-sensitive)
2. Check if you have access to that project in CPD
3. List all projects in CPD web interface to confirm the name

### Error: "node: command not found"

**Solution:** Node.js is not installed or not in PATH. Install Node.js from nodejs.org.

### Error: "Build failed" or TypeScript errors

**Solution:** 
```powershell
# Clean and rebuild
Remove-Item -Recurse -Force build
npm run build
```

### Server Not Appearing in Bob

**Solutions:**
1. Check MCP settings file syntax (valid JSON)
2. Verify the path to `index.js` is correct
3. Check Bob logs for error messages
4. Restart Bob IDE completely

### Performance Issues

**Solutions:**
1. Increase `CACHE_TTL` to reduce API calls
2. Set `LOG_LEVEL` to `warn` or `error` to reduce logging
3. Limit the number of runs requested (use smaller `limit` values)

## Testing the Installation

### Test 1: List Jobs

```
Bob, list all DataStage jobs
```

Expected: List of jobs with their last run status.

### Test 2: Get Job Runs

```
Bob, show me the last 10 runs of [JOB_NAME]
```

Expected: Run history with status, duration, and row counts.

### Test 3: Analyze Failure

```
Bob, analyze why job [JOB_NAME] failed in run [RUN_ID]
```

Expected: Root cause analysis with error details and recommendations.

### Test 4: Generate Report

```
Bob, generate an executive summary report for all jobs this week
```

Expected: Comprehensive report with metrics and insights.

## Updating the Server

To update the server with new features:

```powershell
cd C:\Users\ArfanRusdi\AppData\Roaming\Bob-Code\MCP\datastage-server

# Pull latest changes (if using Git)
git pull

# Reinstall dependencies
npm install

# Rebuild
npm run build

# Restart Bob IDE
```

## Uninstalling

To remove the DataStage MCP server:

1. Remove the server configuration from `mcp_settings.json`
2. Delete the server directory:
   ```powershell
   Remove-Item -Recurse -Force C:\Users\ArfanRusdi\AppData\Roaming\Bob-Code\MCP\datastage-server
   ```
3. Restart Bob IDE

## Security Best Practices

1. **Never commit credentials to Git**
   - Credentials are stored only in MCP settings
   - Add `mcp_settings.json` to `.gitignore` if versioning

2. **Use API keys instead of passwords**
   - API keys can be rotated easily
   - Set expiration dates on keys

3. **Rotate credentials regularly**
   - Regenerate API keys every 90 days
   - Update MCP settings with new keys

4. **Use separate keys for different environments**
   - Dev, test, and prod should have different keys
   - Limit permissions per environment

5. **Monitor access logs**
   - Review CPD audit logs regularly
   - Check for unauthorized access attempts

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review [Architecture Documentation](docs/datastage-mcp-architecture.md)
3. Check server logs (stderr output from Bob)
4. Contact your mentor or DataStage administrator

## Next Steps

After successful installation:

1. Read the [User Guide](docs/USER_GUIDE.md) for usage examples
2. Review the [API Reference](docs/API_REFERENCE.md) for all available tools
3. Try the demo scenarios from [Presentation Pitch](docs/presentation-pitch.md)
4. Customize the server for your specific needs

---

**Congratulations!** Your DataStage MCP Server is now installed and ready to use with Bob IDE.