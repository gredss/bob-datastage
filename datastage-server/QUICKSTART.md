# DataStage MCP Server - Quick Start Guide

Get up and running with the DataStage MCP Server in 5 minutes!

## Prerequisites Check

✅ Node.js 18+ installed  
✅ CPD credentials ready  
✅ Bob IDE installed  

## Installation Steps

### 1. Install Dependencies (2 minutes)

```powershell
cd C:\Users\ArfanRusdi\AppData\Roaming\Bob-Code\MCP\datastage-server
npm install
```

### 2. Build the Server (1 minute)

```powershell
npm run build
```

### 3. Configure Credentials (1 minute)

Create or edit: `C:\Users\ArfanRusdi\.bob\settings\mcp_settings.json`

```json
{
  "mcpServers": {
    "datastage": {
      "command": "node",
      "args": [
        "C:\\Users\\ArfanRusdi\\AppData\\Roaming\\Bob-Code\\MCP\\datastage-server\\build\\index.js"
      ],
      "env": {
        "CPD_URL": "YOUR_CPD_URL_HERE",
        "CPD_API_KEY": "YOUR_API_KEY_HERE",
        "CPD_PROJECT_NAME": "YOUR_PROJECT_NAME_HERE",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

**Replace:**
- `YOUR_CPD_URL_HERE` → Your CPD cluster URL (e.g., `https://cpd-ns.apps.cluster.com`)
- `YOUR_API_KEY_HERE` → Your CPD API key
- `YOUR_PROJECT_NAME_HERE` → Your DataStage project name

### 4. Restart Bob IDE (1 minute)

Close and reopen Bob IDE completely.

### 5. Test It! (30 seconds)

In Bob IDE, try:

```
Bob, list all DataStage jobs
```

You should see a list of your DataStage jobs!

## Quick Test Commands

### List Jobs
```
Bob, list all DataStage jobs
```

### Get Job Runs
```
Bob, show me the last 10 runs of CUSTOMER_LOAD
```

### Analyze Failure
```
Bob, why did job CUSTOMER_LOAD fail in run #12345?
```

### Generate Report
```
Bob, generate an executive summary report for all jobs this week
```

## Troubleshooting

### ❌ "Cannot find module"
**Fix:** Run `npm install` again

### ❌ "Authentication failed"
**Fix:** Check your API key and CPD URL in mcp_settings.json

### ❌ "Project not found"
**Fix:** Verify project name spelling (case-sensitive)

### ❌ Server not appearing in Bob
**Fix:** 
1. Check mcp_settings.json syntax (valid JSON)
2. Verify file path is correct
3. Restart Bob IDE

## Need Help?

- 📖 Full guide: [INSTALLATION.md](INSTALLATION.md)
- 🏗️ Architecture: [docs/datastage-mcp-architecture.md](../../Documents/Automation%20Learning/IBM%20BOB/DataStage/docs/datastage-mcp-architecture.md)
- 💡 Use cases: [docs/presentation-pitch.md](../../Documents/Automation%20Learning/IBM%20BOB/DataStage/docs/presentation-pitch.md)

## What's Next?

1. ✅ Try all 5 tools with your DataStage jobs
2. ✅ Generate your first automated report
3. ✅ Analyze a failed job run
4. ✅ Share results with your mentor
5. ✅ Customize for your team's needs

---

**🎉 Congratulations!** You're now using AI-powered DataStage operations!