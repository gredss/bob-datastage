# 🔄 DataStage ETL/ELT Prompt Builder

Transform natural language prompts into DataStage ETL/ELT workflows using Bob (AI assistant) via Model Context Protocol (MCP).

## 📋 Overview

This application allows users to create DataStage workflows by simply describing what they want in natural language. Bob interprets the prompts and generates structured workflows that are then created in IBM DataStage.

### Architecture

```
User Prompt → Streamlit UI → Bob Orchestrator → MCP Server → DataStage API → Workflow Created
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- IBM DataStage instance with API access
- Valid DataStage API key and project ID

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure DataStage credentials**
   
   The `config.yaml` file is already configured with your credentials:
   - Base URL: `https://cpd-cpd.apps.69cde10d0f861135a8e55d44.ap1.techzone.ibm.com`
   - Project ID: `4efb8e4d-15b2-486c-ba6f-d5c99f3d5272`
   - API Key: Already set (keep secure!)

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Access the UI**
   
   Open your browser to: `http://localhost:8501`

## 📁 Project Structure

```
bob-prompt2etl/
├── streamlit_app.py           # Main Streamlit UI
├── bob_orchestrator.py         # Bridge between UI and Bob/MCP
├── datastage_mcp_server.py     # MCP server for DataStage API
├── config.yaml                 # Configuration (credentials, settings)
├── requirements.txt            # Python dependencies
├── ROADMAP.md                  # Detailed project roadmap
└── README.md                   # This file
```

## 🎯 How to Use

### 1. Enter a Prompt

In the Streamlit UI, describe your ETL/ELT workflow in natural language:

**Example Prompts:**
- "Extract data from CSV file sales.csv, filter by region='North', and load to Snowflake"
- "Read from MySQL table customers, join with orders table, aggregate by customer_id"
- "Extract from PostgreSQL users table, filter active users, transform email to lowercase, load to target database"

### 2. Generate Workflow

Click **"Generate Workflow"** and Bob will:
- Analyze your prompt
- Identify sources, transformations, and targets
- Create a structured workflow plan
- Display the workflow visually

### 3. Review the Plan

The UI will show:
- Workflow steps in sequence
- Node types (connectors, transformations)
- Connections between nodes
- Full workflow definition (JSON)

### 4. Create in DataStage

- Click **"Create in DataStage"**
- Provide a job name (or use auto-generated)
- Confirm creation
- The job will be created in your DataStage project

### 5. Execute and Monitor

- Optionally run the job immediately
- Monitor execution status
- View job details and logs

## 🔧 Configuration

### config.yaml Structure

```yaml
datastage:
  base_url: "https://your-instance.com"
  api_key: "your-api-key"
  project_id: "your-project-id"
  api_version: "v3"
  timeout: 30

mcp:
  server_name: "datastage-mcp-server"
  server_command: "python"
  server_args: ["datastage_mcp_server.py"]

streamlit:
  title: "DataStage ETL/ELT Prompt Builder"
  page_icon: "🔄"
  layout: "wide"
  port: 8501
```

## 🛠️ Components

### 1. Streamlit UI (`streamlit_app.py`)
- User interface for prompt input
- Workflow visualization
- Job creation and monitoring
- Interactive dashboard

### 2. Bob Orchestrator (`bob_orchestrator.py`)
- Bridges Streamlit and MCP
- Parses natural language prompts
- Manages conversation history
- Coordinates workflow creation

### 3. MCP Server (`datastage_mcp_server.py`)
- Exposes DataStage API as MCP tools
- Handles authentication
- Manages API requests/responses
- Tools available:
  - `list_datastage_jobs`
  - `create_datastage_flow`
  - `run_datastage_job`
  - `get_job_status`

## 📊 Supported Workflow Components

### Sources
- CSV/File connectors
- Database connectors (MySQL, PostgreSQL, etc.)
- Cloud storage connectors

### Transformations
- Filter
- Aggregator
- Join
- Sort
- Lookup

### Targets
- Database writers
- Snowflake connector
- Cloud storage writers
- File writers

## 🔐 Security Notes

⚠️ **Important Security Considerations:**

1. **API Key Protection**
   - Never commit `config.yaml` to public repositories
   - Use environment variables in production
   - Rotate API keys regularly

2. **Access Control**
   - Limit API key permissions to necessary operations
   - Use separate keys for dev/staging/production
   - Monitor API usage

3. **Network Security**
   - Run on secure networks
   - Use HTTPS for DataStage connections
   - Consider VPN for remote access

## 🐛 Troubleshooting

### Common Issues

**1. MCP Import Errors**
```bash
# Install MCP package
pip install mcp
```

**2. Connection Timeout**
- Check DataStage instance URL
- Verify network connectivity
- Increase timeout in config.yaml

**3. Authentication Failed**
- Verify API key is correct
- Check API key permissions
- Ensure project ID is valid

**4. Streamlit Not Starting**
```bash
# Reinstall streamlit
pip install --upgrade streamlit
```

## 📈 Future Enhancements

- [ ] Full Bob integration via MCP (currently simplified)
- [ ] More sophisticated prompt parsing
- [ ] Support for complex transformations
- [ ] Workflow templates library
- [ ] Job scheduling capabilities
- [ ] Real-time execution monitoring
- [ ] Workflow version control
- [ ] Multi-user support with authentication

## 🤝 Contributing

This is a proof-of-concept implementation. To extend:

1. Enhance `bob_orchestrator.py` with actual MCP communication
2. Add more DataStage API operations in `datastage_mcp_server.py`
3. Improve prompt parsing with NLP/LLM capabilities
4. Add more workflow components and transformations

## 📝 Example Workflows

### Example 1: Simple ETL
**Prompt:** "Read sales.csv, filter by amount > 1000, write to database"

**Generated Workflow:**
```
CSV Reader → Filter (amount > 1000) → Database Writer
```

### Example 2: Data Integration
**Prompt:** "Join customers and orders tables, aggregate total sales by customer"

**Generated Workflow:**
```
DB Reader (customers) ─┐
                       ├─→ Join → Aggregator → DB Writer
DB Reader (orders) ────┘
```

### Example 3: Cloud Migration
**Prompt:** "Extract from MySQL, transform data types, load to Snowflake"

**Generated Workflow:**
```
MySQL Reader → Transformer → Snowflake Writer
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review DataStage API documentation
3. Check MCP documentation at https://modelcontextprotocol.io

## 📄 License

This is a demonstration project. Ensure compliance with IBM DataStage licensing terms.

---

**Built with:**
- 🤖 Bob (AI Assistant)
- 🔄 IBM DataStage
- 🎨 Streamlit
- 🔌 Model Context Protocol (MCP)
- 🐍 Python

**Version:** 1.0.0  
**Last Updated:** April 2026