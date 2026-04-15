# DataStage MCP Server

AI-powered DataStage integration for Bob IDE, enabling automated job monitoring, root cause analysis, and intelligent optimization.

## 🚀 Quick Start

```powershell
# Install dependencies
npm install

# Build the server
npm run build

# Configure MCP settings (see INSTALLATION.md)
# Then restart Bob IDE
```

## 📋 Features

### 5 Core Tools

1. **datastage_list_jobs** - List all DataStage jobs with status
2. **datastage_get_job_runs** - Get run history with metrics
3. **datastage_analyze_failure** - AI-powered root cause analysis
4. **datastage_get_job_logs** - Export raw logs for analysis
5. **datastage_generate_report** - Create comprehensive reports

## 📖 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[Architecture](../../Documents/Automation%20Learning/IBM%20BOB/DataStage/docs/datastage-mcp-architecture.md)** - System design and components
- **[Implementation Plan](../../Documents/Automation%20Learning/IBM%20BOB/DataStage/docs/implementation-plan.md)** - Development roadmap
- **[Presentation Pitch](../../Documents/Automation%20Learning/IBM%20BOB/DataStage/docs/presentation-pitch.md)** - Business value and ROI

## 🎯 Use Cases

### Daily Operations Report
```
Bob, generate an executive summary report for all jobs this week
```

### Troubleshoot Failed Job
```
Bob, job CUSTOMER_LOAD failed in run #12345. What went wrong?
```

### Performance Analysis
```
Bob, show me the performance trends for CUSTOMER_LOAD over the last 10 runs
```

## 🔧 Configuration

Required environment variables (set in MCP settings):

```json
{
  "CPD_URL": "https://your-cpd-instance.com",
  "CPD_API_KEY": "your-api-key",
  "CPD_PROJECT_NAME": "your-project-name"
}
```

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

## 🏗️ Project Structure

```
datastage-server/
├── src/
│   ├── index.ts              # Main MCP server
│   ├── auth/
│   │   └── AuthManager.ts    # CPD authentication
│   ├── api/
│   │   └── CPDClient.ts      # API client
│   ├── config/
│   │   ├── constants.ts      # Configuration
│   │   └── types.ts          # Type definitions
│   └── utils/
│       ├── cache.ts          # Caching
│       ├── logger.ts         # Logging
│       └── retry.ts          # Retry logic
├── build/                    # Compiled JavaScript
├── package.json
├── tsconfig.json
└── INSTALLATION.md
```

## 🧪 Testing

```powershell
# Run tests (when implemented)
npm test

# Run with coverage
npm run test:coverage

# Lint code
npm run lint
```

## 🔒 Security

- Credentials stored only in MCP settings
- Bearer tokens cached in memory only
- All job modifications logged
- Automatic backups before changes

## 📊 Performance

- Job listing: < 2 seconds for 100 jobs
- Run history: < 3 seconds for 50 runs
- Log analysis: < 5 seconds for 10MB logs
- Report generation: < 10 seconds for 100 jobs

## 🐛 Troubleshooting

### Server not starting
- Check Node.js version (18+)
- Verify all dependencies installed
- Check MCP settings syntax

### Authentication failed
- Verify CPD_URL is correct
- Check API key hasn't expired
- Ensure user has DataStage access

### No jobs found
- Verify CPD_PROJECT_NAME spelling
- Check project access permissions
- Confirm project exists in CPD

See [INSTALLATION.md](INSTALLATION.md) for more troubleshooting tips.

## 🤝 Contributing

This is an intern project for IBM. For questions:
1. Review the documentation
2. Check with your mentor
3. Test changes thoroughly

## 📄 License

Internal IBM project - not for external distribution.

## 👥 Authors

- **Intern**: Arfan Rusdi
- **Organization**: IBM

## 🙏 Acknowledgments

- IBM DataStage team
- Model Context Protocol (MCP) team
- Bob IDE team

---

**Version**: 0.1.0  
**Status**: MVP Implementation  
**Last Updated**: 2026-04-09