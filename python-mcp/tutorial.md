# Building an IBM DataStage MCP Server from Scratch with IBM BOB (Python Edition)

Welcome! This tutorial will help you build a custom IBM DataStage Model Context Protocol (MCP) server using Python and FastMCP. We'll walk through the entire process, from setting up your environment to deploying your server and testing it. By the end, you'll have a fully functional MCP server with dynamic project selection that integrates seamlessly with IBM BOB. Let's get started!

---

## Table of Contents

1. [Prepare the IBM DataStage Environment and Credentials](#step-1-prepare-the-ibm-datastage-environment-and-credentials)
   - [1.1 Reserve the Environment](#11-reserve-the-environment)
   - [1.2 Navigate to the DataStage Environment and Get Credentials](#12-navigate-to-the-datastage-environment-and-get-credentials)
   - [1.3 Creating Assets](#13-creating-assets)
2. [Creating the MCP Server with IBM Bob](#step-2-creating-the-mcp-server-with-ibm-bob)
   - [2.1 Exploring the API Documentation and Extracting cURL Commands](#21-exploring-the-api-documentation-and-extracting-curl-commands)
   - [2.2 Prompting Bob](#22-prompting-bob)
   - [2.3 What Bob Creates](#23-what-bob-creates)
3. [Understanding the Generated Architecture](#step-3-understanding-the-generated-architecture)
   - [The Request Flow](#the-request-flow)
   - [Key Architectural Decisions Bob Made](#key-architectural-decisions-bob-made)
   - [Understanding Python Project Structure](#understanding-python-project-structure)
4. [Secure Configuration & Setup](#step-4-secure-configuration--setup)
   - [4.1 Install Python Dependencies](#41-install-python-dependencies)
   - [4.2 Understanding Python Packages](#42-understanding-python-packages)
   - [4.3 Configure Bob's MCP Settings](#43-configure-bobs-mcp-settings)
5. [Dynamic Project Selection](#step-5-dynamic-project-selection)
   - [5.1 Why Dynamic Project Selection?](#51-why-dynamic-project-selection)
   - [5.2 How It Works](#52-how-it-works)
   - [5.3 Using Dynamic Projects](#53-using-dynamic-projects)
6. [Testing the Integration](#step-6-testing-the-integration)
   - [6.1 Test Prompt 1: List Available Projects](#61-test-prompt-1-list-available-projects)
   - [6.2 Test Prompt 2: Select and List Jobs](#62-test-prompt-2-select-and-list-jobs)
   - [6.3 Test Prompt 3: Run a Job](#63-test-prompt-3-run-a-job)
   - [6.4 Test Prompt 4: Export and Import Flows](#64-test-prompt-4-export-and-import-flows)
   - [6.5 Advanced Testing](#65-advanced-testing)
7. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [Debugging Tips](#debugging-tips)
8. [Conclusion](#conclusion)
   - [What You've Learned](#what-youve-learned)
   - [The Power of AI-Assisted Development](#the-power-of-ai-assisted-development)
   - [Next Steps](#next-steps)

---

## Step 1: Prepare the IBM DataStage Environment and Credentials

Before building our MCP server, we need a live DataStage environment to connect to. We will use IBM TechZone to reserve an instance of IBM DataStage.

### 1.1 Reserve the Environment

1. Navigate to the **IBM TechZone** portal and log in with your IBM credentials.
2. In the search bar, look for **DataStage Level 3** and click on the **IBM Cloud Environment** button on the pre-warmed environment.

   ![Search DataStage in TechZone](asset/TechZone_portal.png)

3. Inside the reservation page, fill in the following details:
   - **Name:** Datastage Level 3
   - **Purpose:** Education
   - **Purpose Description:** Datastage Level 3
   - **Preferred Region Template:** {your preferred region}

   ![Fill Reservation Details](asset/Reserve_DS.png)

4. Check the "I agree" box on the bottom right, then click **Submit**. For a pre-warmed environment, provisioning takes a couple of minutes.

### 1.2 Navigate to the DataStage Environment and Get Credentials

1. Once you receive the confirmation email that your environment is ready, open your TechZone environment details page.
2. Copy the **kubeadmin** password displayed on the page, then click the **Open Your IBM Cloud Environment** button.

   ![Navigate to DataStage Environment](asset/DS_Env.png)

3. On the login screen, select the **kube:admin** authentication option and log in using the password you just copied.

   ![Select kubeadmin](asset/kubeadmin_1.png)
   ![Login Screen](asset/kubeadmin_2.png)

4. After logging in, look at the left-hand navigation menu. Expand the **Pipelines** section, click on **PipelineRuns**, and select the single active pipeline currently running in the list.

   ![Navigate to PipelineRuns](asset/pipelines.png)

5. Inside the pipeline run details, open the **Logs** tab. There you will see the details of your Cloud Pak for Data instance. **Copy and save these somewhere safe:**
   - **Console Route:** Your CPD URL
   - **Username:** Your CPD username
   - **Password:** Your CPD password

   ![Extract CPD Credentials](asset/CPD_creds.png)

6. Copy the Console Route URL and open it in your web browser. Log in with your CPD username and password.

   ![CPD Login Screen](asset/CPD_login.png)

7. Click the **New project** button.

   ![Create CPD Project](asset/CPD_create_project.png)

8. Enter a name for your project and click **Create**.

   ![Name CPD Project](asset/CPD_project.png)

9. (Optional) To set a default project, head into your project page, and in the URL, you will see your `project_id`. You can save this to use as the default `CPD_PROJECT_ID` environment variable.

   ![Extract Project ID](asset/CPD_projectid.png)

### 1.3 Creating Assets

For this tutorial, we will provide the assets for you to use by importing them into your project.

1. Click the **Assets** tab, then click **New asset**.

   ![Assets Tab](asset/assets.png)

2. Click **Transform and integrate data**.

   ![Transform and Integrate Data](asset/new_asset.png)

3. Click **Local file** and upload the `Employee_Ranking_Export.zip` file we provided.

   ![Upload Zip File](asset/drop_zip.png)

4. You would see a success message when the zip file is uploaded successfully, and the flow will be visible to use.

   ![Import Success](asset/import_success.png)

**Congrats!** You have completed step 1. Now we will look into how we can make an IBM DataStage MCP server with IBM Bob using Python.

---

## Step 2: Creating the MCP Server with IBM Bob

IBM Bob has the built-in capability to automatically generate custom MCP servers for you. First, ensure this feature is active by navigating to the **MCP Settings** tab in IBM Bob and verifying that **Enable MCP Server Creation** is turned on.

![MCP Settings](asset/MCP_settings.png)

Before prompting Bob to write the code, we need a clear plan. We must define exactly which DataStage operations (tools) we want our AI to be capable of executing. For this tutorial, we will build an MCP server with the following tools:

- List projects
- Select project
- List jobs
- Get job runs
- Get job run logs
- List flows
- Get flow details
- Export a flow
- Import a flow
- Compile a flow
- Run a job
- Convert flow to Python SDK code

### 2.1 Exploring the API Documentation and Extracting cURL Commands

After defining our required tools, we must verify that these operations are supported by IBM DataStage's REST API and identify their specific endpoints. You can reference the official API Documentation for IBM DataStage [here](https://dataplatform.cloud.ibm.com/docs/content/dstage/dsnav/topics/ds-apis.html?context=cpdaas&audience=wdp).

For job-specific APIs, you can click the **Jobs** hyperlink within the documentation. For APIs related to flows and assets, click the **DataStage** hyperlink. For project listing, check the **Projects** API.

For this tutorial example, click **Jobs**.

![API Documentation](asset/API.png)

As you can see, the Jobs API page shows all the endpoints available for job-related operations. We can already verify that the endpoints to list jobs, get job runs, get job run logs, and run a job are all available on this page.

![Jobs API](asset/jobs_api.png)

Now, click on the `/v2/jobs` endpoint to expand its details. This section displays the required parameters alongside examples of the API request and response.

![List Jobs API](asset/list_jobs_api.png)

A best practice before prompting IBM Bob is to grab an example cURL request directly from this documentation. Providing the cURL command gives Bob the exact endpoint structure and payload format it needs to write accurate code.

To generate and copy the cURL example, follow these steps:

1. Scroll to the top of the documentation page and click the **Authorize** button.

   ![Jobs API Authorize](asset/Authorize.png)

2. Enter `bearer_token` as a placeholder value and click **Authorize**. *(Note: You do not need an actual token here; we just need the placeholder to generate the correct cURL syntax).*

   ![Jobs API Bearer Token](asset/bearer_token.png)

3. Navigate back to the `/v2/jobs` endpoint block and click the **Try it out** button.

   ![Jobs API Try It Out](asset/try_it_out.png)

4. You will now be able to fill in the API parameters. Enter `project_id` as a placeholder value in the **project_id** field.

   ![Jobs API Project ID](asset/project_id_param.png)

5. Scroll down and click the **Execute** button.

   ![Jobs API Execute](asset/execute.png)

6. You will now see the generated cURL request in the UI. You can ignore the server response block (which will show an error), as our only goal was to extract this exact cURL command.

   ![Jobs API Curl Example](asset/curl_example.png)

**Repeat for All Required Endpoints:**

Repeat the cURL extraction process for each of the tools you want to implement. For this tutorial, you should extract cURL commands for:

- `/v2/projects` (List projects) - **available in https://cloud.ibm.com/apidocs/data-ai-common-core**
- `/v2/jobs` (List jobs)
- `/v2/jobs/{job_id}/runs` (Get job runs)
- `/v2/jobs/{job_id}/runs/{run_id}/logs` (Get job run logs)
- `/v2/jobs/{job_id}/runs` with POST method (Run a job)
- `/data_intg/v3/data_intg_flows` (List flows)
- `/data_intg/v3/data_intg_flows/{data_intg_flow_id}` (Get flow details)
- `/data_intg/v3/migration/zip_exports` (Export a flow)
- `/data_intg/v3/migration/zip_imports` (Import a flow)
- `/data_intg/v3/ds_codegen/compile/{flow_id}` (Compile a flow)

Once you have collected all the cURL commands, you're ready to construct your prompt for Bob.

### 2.2 Prompting Bob

Now that you have all the cURL commands, it's time to combine them into a comprehensive prompt for IBM Bob. The key is to provide Bob with clear requirements about what you want the MCP server to do, along with the API examples.

Here's an example of what your prompt should look like:

```
Bob, I need you to build a Python MCP server for IBM DataStage using FastMCP.

REQUIREMENTS:
- Use Python 3.8+ with FastMCP framework
- The server needs to authenticate with Cloud Pak for Data using username and password to get a Bearer token
- It should handle token expiration and automatically refresh when needed
- Include retry logic for failed API requests with exponential backoff
- Add caching to avoid redundant API calls
- Use proper error handling and logging
- Make the code maintainable with type hints
- Support dynamic project selection (users can list and select projects at runtime)
- Make CPD_PROJECT_ID optional in environment variables

TOOLS TO IMPLEMENT:
1. list_projects - List all available DataStage projects
2. select_project - Set the default project for subsequent operations
3. list_jobs - List all DataStage jobs in a project
4. get_job_runs - Get execution history for a specific job
5. get_job_run_logs - Retrieve logs for a specific job run
6. run_job - Execute a DataStage job
7. list_flows - List all DataStage flows in a project
8. get_flow_details - Get detailed information about a specific flow
9. export_flow - Export a flow as a zip file
10. import_flow - Import a flow from a zip file
11. compile_flow - Compile a DataStage flow
12. convert_flow_to_python - Convert exported flow to Python SDK code

CURL EXAMPLES:
Here are the cURL commands for each endpoint:

[Paste all your extracted cURL commands here, one for each tool]

ENVIRONMENT VARIABLES:
The server should read these from environment variables:
- CPD_URL: The Cloud Pak for Data base URL
- CPD_USERNAME: CPD username
- CPD_PASSWORD: CPD password

PROJECT STRUCTURE:
Organize the code into a clean Python package structure:
- src/server.py - Main FastMCP server with tool definitions
- src/api/cpd_client.py - API client for CPD
- src/auth/auth_manager.py - Authentication management
- src/config/constants.py - Configuration and constants
- src/utils/ - Utility modules (cache, logger, retry)

Please generate a complete, production-ready implementation with proper Python packaging.
```

After you send this prompt to Bob, sit back and watch the magic happen. Bob will analyze your requirements, understand the API structure from the cURL examples, and generate a complete MCP server implementation. `(Note: You can prompt Bob to create your MCP server gradually step by step instead of 1 big prompt)`

### 2.3 What Bob Creates

Bob will generate a well-structured Python project with multiple files organized into a clean architecture. Here's what Bob created for this DataStage MCP server:

```
datastage-mcp/
├── python/
│   ├── src/
│   │   ├── __init__.py           # Package initialization
│   │   ├── server.py             # Main FastMCP server
│   │   ├── auth/
│   │   │   ├── __init__.py       # Auth package init
│   │   │   └── auth_manager.py   # CPD authentication
│   │   ├── api/
│   │   │   ├── __init__.py       # API package init
│   │   │   └── cpd_client.py     # API client
│   │   ├── config/
│   │   │   ├── __init__.py       # Config package init
│   │   │   └── constants.py      # Configuration
│   │   └── utils/
│   │       ├── __init__.py       # Utils package init
│   │       ├── cache.py          # Caching
│   │       ├── logger.py         # Logging
│   │       └── retry.py          # Retry logic
│   ├── generated_code/           # Output for converted flows
│   ├── run_server.py             # Server entry point
│   ├── requirements.txt          # Python dependencies
│   ├── pyproject.toml            # Project metadata
│   └── README.md                 # Documentation
```

**Core Server File:**
- `src/server.py` - The main FastMCP server that registers all tools and handles incoming requests from IBM Bob
- `run_server.py` - Entry point script that starts the MCP server

**API Layer:**
- `src/api/cpd_client.py` - The client that communicates with Cloud Pak for Data APIs, handling all HTTP requests and responses

**Authentication:**
- `src/auth/auth_manager.py` - Manages Bearer token authentication, including login, token storage, and automatic refresh

**Utilities:**
- `src/utils/retry.py` - Implements retry logic with exponential backoff for handling transient failures
- `src/utils/cache.py` - Provides authentication token caching to avoid redundant login requests
- `src/utils/logger.py` - Centralized logging utility for debugging and monitoring

**Configuration:**
- `src/config/constants.py` - Stores API endpoints, timeout values, and other constants

**Project Files:**
- `requirements.txt` - Python package dependencies
- `pyproject.toml` - Modern Python project metadata and build configuration
- `README.md` - Documentation for the MCP server

Bob has essentially created a production-ready MCP server with enterprise-grade features like authentication management, retry logic, caching, dynamic project selection, and comprehensive error handling—all without you having to write a single line of code!

---

## Step 3: Understanding the Generated Architecture

Now that Bob has created your MCP server, let's understand how it works. Think of the generated code as a well-organized system where each component has a specific responsibility.

### The Request Flow

When you ask Bob a question like "Show me all DataStage jobs," here's what happens behind the scenes:

1. **Bob sends the request** to your MCP server through the `run_server.py` entry point
2. **FastMCP routes** the request to the appropriate tool in `server.py`
3. **The server identifies** which tool to use (in this case, `datastage_list_jobs`)
4. **AuthManager checks** if we have a valid Bearer token; if not, it logs in to CPD and gets one
5. **Token is cached** (ONLY the Bearer token, NOT API responses) to avoid redundant logins
6. **CPDClient constructs** the appropriate API request using the stored token
7. **Retry logic** attempts the HTTP call, automatically retrying if there are temporary failures
8. **The response flows back** through the chain to Bob (API responses are NOT cached)
9. **Logger records** the entire transaction for debugging

**Important Note on Caching:** The cache layer ONLY stores authentication tokens. API responses are NOT cached - every API call fetches fresh data from CPD. This ensures you always get the latest job statuses, flow definitions, and run logs.

### Key Architectural Decisions Bob Made

**Separation of Concerns:** Bob separated authentication, API calls, utilities, and configuration into distinct modules. This makes the code easier to maintain and test.

**Token Management:** Instead of logging in for every request, Bob created an AuthManager that stores the Bearer token and only refreshes it when needed. This improves performance and reduces load on the CPD server.

**Dynamic Project Selection:** Bob implemented a 3-tier priority system for project selection:
1. Explicit `project_id` parameter in tool calls
2. Selected project via `datastage_select_project` tool
3. Environment variable `CPD_PROJECT_ID`

This means users can work with multiple projects without restarting the server!

**Resilience:** The retry logic means temporary network glitches won't break your workflows. Bob automatically retries failed requests with smart delays.

**Performance:** The caching layer stores authentication tokens to avoid redundant login requests. Once authenticated, the token is reused until it expires, reducing load on the CPD server.

**Type Safety:** Bob used Python type hints throughout, which means you get better IDE support and catch errors earlier.

**Async/Await:** Bob used Python's async/await pattern for non-blocking I/O operations, making the server more efficient.

This architecture wasn't something you had to design—Bob analyzed your requirements and the API structure, then made intelligent decisions about how to build a robust, maintainable system.

### Understanding Python Project Structure

Let's dive deeper into the Python-specific aspects of the project:

#### The `__init__.py` Files

You'll notice `__init__.py` files in every directory under `src/`. These files serve several purposes:

1. **Package Markers:** They tell Python that the directory should be treated as a package
2. **Namespace Control:** They can control what gets imported when you do `from package import *`
3. **Initialization Code:** They can run initialization code when the package is imported

In our project, most `__init__.py` files are empty, which is fine—they're just marking the directories as packages.

#### The `__pycache__` Directories

When you run Python code, you'll see `__pycache__` directories appear. These contain:

- **Bytecode files** (`.pyc` files) - Compiled Python code
- **Faster startup** - Python doesn't need to recompile the source code
- **Version-specific** - Different Python versions create different bytecode

You can safely ignore these directories—they're automatically generated and managed by Python.

#### `requirements.txt` vs `pyproject.toml`

**requirements.txt:**
- Traditional way to list Python dependencies
- Simple format: one package per line
- Used by `pip install -r requirements.txt`
- Example:
  ```
  fastmcp==0.1.0
  httpx==0.27.0
  python-dotenv==1.0.0
  ```

**pyproject.toml:**
- Modern Python project configuration
- Follows PEP 518 standard
- Can include metadata, build settings, and dependencies
- More structured and feature-rich
- Example:
  ```toml
  [project]
  name = "datastage-mcp-server"
  version = "1.0.0"
  dependencies = [
      "fastmcp>=0.1.0",
      "httpx>=0.27.0"
  ]
  ```

Our project includes both for maximum compatibility!

#### Python Virtual Environments

When working with Python projects, it's best practice to use virtual environments:

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Virtual environments keep your project dependencies isolated from other Python projects.

#### Type Hints in Python

Bob used type hints throughout the code. Here's what they mean:

```python
async def list_jobs(self, project_id: Optional[str] = None) -> Any:
    """
    List all runtime jobs in the project
    
    Args:
        project_id: Optional project ID
    
    Returns:
        Dictionary containing jobs list
    """
```

- `project_id: Optional[str]` - Parameter can be a string or None
- `-> Any` - Function returns any type
- Type hints help IDEs provide better autocomplete and catch errors

#### Async/Await Pattern

Bob used Python's async/await for efficient I/O operations:

```python
async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
    """Make an authenticated HTTP request"""
    token = await self.auth_manager.get_token()  # Wait for token
    # ... make request
```

- `async def` - Defines an asynchronous function
- `await` - Waits for an async operation to complete
- Allows multiple operations to run concurrently
- More efficient than blocking I/O

---

## Step 4: Secure Configuration & Setup

Now that Bob has generated your MCP server code, it's time to configure it with your credentials and set it up.

### 4.1 Install Python Dependencies

First, ensure you have Python 3.10 or higher installed:

```bash
python --version
```

Navigate to your project directory and install the required packages:

```bash
# Optional but recommended: Create a virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

This installs all the packages Bob specified in `requirements.txt`, including:
- `fastmcp` - The FastMCP framework for building MCP servers
- `httpx` - Modern async HTTP client for API requests
- `pydantic` - Data validation and settings management
- `ibm-watsonx-data-integration` - IBM DataStage Python SDK (for flow conversion)

### 4.2 Understanding Python Packages

Let's understand what each package does:

**FastMCP:**
- Framework for building Model Context Protocol servers
- Provides decorators like `@mcp.tool()` to define tools
- Handles communication with MCP clients (like Bob)
- Manages tool registration and execution

**httpx:**
- Modern HTTP client with async support
- Used for making API calls to Cloud Pak for Data
- Supports connection pooling and timeouts
- Better than `requests` for async operations

**pydantic:**
- Data validation and settings management using Python type annotations
- Ensures data integrity and type safety
- Used by FastMCP for request/response validation

**ibm-watsonx-data-integration:**
- Official IBM DataStage Python SDK
- Used by the `convert_flow_to_python` tool
- Allows programmatic creation and modification of DataStage flows

### 4.3 Configure Bob's MCP Settings

Now tell IBM Bob where to find your Python MCP server:

1. Open IBM Bob's MCP Settings
2. Locate the `mcp_settings.json` configuration file
3. Add your DataStage MCP server configuration:

```json
{
  "mcpServers": {
    "datastage-python": {
      "command": "python",
      "args": [
        "{your_path}/python/run_server.py"
      ],
      "env": {
        "CPD_URL": "https://your-cpd-instance.com",
        "CPD_USERNAME": "your_username",
        "CPD_PASSWORD": "your_password"
      }
    }
  }
}
```

**Important Notes:**
- Replace the path in `args` with the absolute path to your `run_server.py` file
- Replace the `env` values with your actual CPD credentials from Step 1
- **CPD_PROJECT_ID is now optional!** You can list and select projects dynamically
- The server name `"datastage-python"` can be customized
- On Windows, use forward slashes or double backslashes in paths

**Example with Optional Project ID:**

```json
{
  "mcpServers": {
    "datastage-python": {
      "command": "python",
      "args": [
        "C:/Users/YourName/datastage-mcp/python/run_server.py"
      ],
      "env": {
        "CPD_URL": "https://cpd-cpd.apps.example.com",
        "CPD_USERNAME": "admin",
        "CPD_PASSWORD": "your_secure_password",
        "CPD_PROJECT_ID": "50d10fa5-4d57-46b6-9b79-fe3ea1574275"
      }
    }
  }
}
```

**Example without Project ID (Dynamic Selection):**

```json
{
  "mcpServers": {
    "datastage-python": {
      "command": "python",
      "args": [
        "C:/Users/YourName/datastage-mcp/python/run_server.py"
      ],
      "env": {
        "CPD_URL": "https://cpd-cpd.apps.example.com",
        "CPD_USERNAME": "admin",
        "CPD_PASSWORD": "your_secure_password"
      }
    }
  }
}
```

4. Save the `mcp_settings.json` file
5. Restart IBM Bob to load the new configuration

Bob will now automatically start your DataStage MCP server when needed and communicate with it to execute DataStage operations.

---

## Step 5: Dynamic Project Selection

One of the most powerful features of this MCP server is dynamic project selection. Let's understand how it works!

### 5.1 Why Dynamic Project Selection?

**Before (Hardcoded Project ID):**
- Had to manually find and copy project_id from CPD UI
- Needed to restart server to switch projects
- Couldn't work with multiple projects in one session
- Required updating `mcp_settings.json` for each project change

**After (Dynamic Selection):**
- ✅ List all available projects with one command
- ✅ Switch between projects without restarting
- ✅ Work with multiple projects in a single session
- ✅ No need to manually copy project IDs
- ✅ Better user experience and flexibility

### 5.2 How It Works

The MCP server implements a **3-tier priority system** for project selection:

```
Priority 1: Explicit project_id parameter
    ↓ (if not provided)
Priority 2: Selected project via datastage_select_project
    ↓ (if not selected)
Priority 3: Environment variable CPD_PROJECT_ID
    ↓ (if not set)
Error: "No project ID available"
```

**Example Flow:**

```python
# In cpd_client.py
async def _get_project_id(self, project_id: Optional[str] = None) -> str:
    # Priority 1: Explicit parameter
    if project_id:
        return project_id
    
    # Priority 2: Selected project
    if self._selected_project_id:
        return self._selected_project_id
    
    # Priority 3: Environment variable
    if ENV.CPD_PROJECT_ID:
        return ENV.CPD_PROJECT_ID
    
    # No project available
    raise Exception('No project ID available...')
```

### 5.3 Using Dynamic Projects

**Workflow 1: List and Select Once**

```
User: "List all my DataStage projects"
Bob: [Calls datastage_list_projects]
     Shows: Project A (id: abc-123), Project B (id: def-456)

User: "Select Project A"
Bob: [Calls datastage_select_project with id: abc-123]
     Confirms: "Project A selected"

User: "List all jobs"
Bob: [Calls datastage_list_jobs - uses selected project]
     Shows: Jobs from Project A

User: "List all flows"
Bob: [Calls datastage_list_flows - still uses Project A]
     Shows: Flows from Project A
```

**Workflow 2: Override Per Operation**

```
User: "Select Project A"
Bob: [Selects Project A as default]

User: "List jobs from Project B"
Bob: [Calls datastage_list_jobs with explicit project_id for Project B]
     Shows: Jobs from Project B

User: "List flows"
Bob: [Calls datastage_list_flows - uses default Project A]
     Shows: Flows from Project A
```

**Workflow 3: Environment Variable Fallback**

```
# In mcp_settings.json
"env": {
  "CPD_PROJECT_ID": "abc-123"
}

User: "List all jobs"
Bob: [Uses CPD_PROJECT_ID from environment]
     Shows: Jobs from default project

User: "Select Project B"
Bob: [Overrides environment variable]
     Now uses Project B for subsequent calls
```

---

## Step 6: Testing the Integration

Your DataStage MCP server is now live! Let's test it with natural language prompts, starting with the new dynamic project selection features.

### 6.1 Test Prompt 1: List Available Projects

Open a new chat with Bob and try:

```
Show me all the DataStage projects I have access to.
```

**What happens behind the scenes:**
1. Bob recognizes this requires the `datastage_list_projects` tool
2. Bob calls your MCP server
3. Your AuthManager checks for a cached token; if none exists, it logs into CPD and gets a Bearer token (which is then cached)
4. CPDClient makes the API request to `/v2/projects` using the token
5. The response is formatted to show project names and IDs
6. Bob presents the results in a readable format

You should see a list of all projects you have access to, including:
- Project ID (the unique identifier)
- Project name
- Description
- Creation date
- BSS Account ID (if applicable)

**Example Response:**
```
I found 2 DataStage projects:

1. Datastage_Project
   - ID: 50d10fa5-4d57-46b6-9b79-fe3ea1574275
   - Created: 2026-05-05
   
2. Development_Project
   - ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   - Created: 2026-04-15
```

### 6.2 Test Prompt 2: Select and List Jobs

Now select a project and list its jobs:

```
Select the Datastage_Project and show me all the jobs in it.
```

**What happens behind the scenes:**
1. Bob uses `datastage_select_project` with the project ID
2. The server stores this as the default project
3. Bob uses `datastage_list_jobs` (without specifying project_id)
4. The server uses the selected project automatically
5. Bob presents the job list

You should see all jobs in the selected project, including the "RowGenPeek" job you imported in Step 1.

### 6.3 Test Prompt 3: Run a Job

Try executing a job:

```
Run the RowGenPeek job and show me the execution status.
```

**What happens behind the scenes:**
1. Bob uses `datastage_list_jobs` to find the job ID for "RowGenPeek"
2. Bob uses `datastage_run_job` to execute it
3. Bob may use `datastage_get_job_runs` to check the status
4. Bob reports back with the run ID and current status

This demonstrates Bob's ability to chain multiple tool calls together intelligently to accomplish a complex task—something you didn't have to program explicitly!

### 6.4 Test Prompt 4: Export and Import Flows

Try exporting and importing flows:

```
Export the RowGenPeek flow and save it as a zip file.
```

**What happens behind the scenes:**
1. Bob uses `datastage_list_flows` to find the flow ID
2. Bob uses `datastage_export_flow` to download the flow as a zip file
3. Bob saves the file to your local filesystem
4. Bob confirms the export was successful

Then try importing:

```
Import the RowGenPeek.zip file with rename conflict resolution.
```

**What happens behind the scenes:**
1. Bob uses `datastage_import_flow` with the zip file path
2. The server uploads the file to CPD
3. CPD processes the import asynchronously
4. Bob reports the import ID and status

### 6.5 Advanced Testing

Once basic operations work, try more complex scenarios:

**Multi-Project Operations:**
```
Compare the number of jobs in Datastage_Project versus Development_Project.
```

**Flow Conversion:**
```
Convert the RowGenPeek flow to Python SDK code and save it to the generated_code folder.
```

**Job Monitoring:**
```
Show me the logs from the most recent run of the RowGenPeek job.
```

**Complex Workflows:**
```
Export all flows from Datastage_Project, then list their names and sizes.
```

These prompts test Bob's ability to:
- Work with multiple projects dynamically
- Chain multiple API calls
- Filter and analyze data
- Present insights in natural language
- Convert DataStage flows to Python code

All of this works because of the robust MCP server Bob generated for you!

---

## Troubleshooting

### Common Issues

**Issue: "Authentication failed"**
- Verify your CPD credentials in the `mcp_settings.json`
- Check that your CPD instance is accessible from your network
- Ensure your CPD password hasn't expired
- Try logging in manually to CPD to verify credentials

**Issue: "No project ID available"**
- Use `datastage_list_projects` to see available projects
- Use `datastage_select_project` to select a project
- Or set `CPD_PROJECT_ID` in your environment variables

**Issue: "MCP server not responding"**
- Check that the path to `run_server.py` in `mcp_settings.json` is correct
- Ensure Python is in your system PATH
- Verify all dependencies are installed (`pip list`)
- Restart IBM Bob after configuration changes

**Issue: "Module not found" errors**
- Run `pip install -r requirements.txt` again
- Check that you're using the correct Python environment
- Verify your virtual environment is activated (if using one)

**Issue: "Import flow failed with list index out of range"**
- This was a known issue that has been fixed
- Make sure you're using the latest version of the code
- The server now safely handles empty import_data_flows arrays

**Issue: "SSL certificate verification failed"**
- The server disables SSL verification for self-signed certificates
- If you need to enable it, modify the `verify=False` parameter in `cpd_client.py`

### Debugging Tips

1. **Check the logs:** Bob's generated logger writes important information. Look for error messages in Bob's output.

2. **Test the API directly:** Use tools like Postman or curl to verify your CPD instance is responding correctly:
   ```bash
   curl -X POST "https://your-cpd-url/icp4d-api/v1/authorize" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"your_password"}'
   ```

3. **Verify environment variables:** The logger will show if environment variables are missing or incorrect.

4. **Test Python imports:** Run Python interactively and try importing the modules:
   ```python
   from src.server import mcp
   from src.api.cpd_client import CPDClient
   ```

5. **Check Python version:** Ensure you're using Python 3.8 or higher:
   ```bash
   python --version
   ```

6. **Inspect the cache:** The cache is stored in memory. If you're getting stale data, restart the MCP server.

7. **Enable debug logging:** Modify `src/utils/logger.py` to set log level to DEBUG for more detailed output.

---

## Conclusion

You've successfully built a custom MCP server that bridges IBM Bob with IBM DataStage using Python! This integration allows you to:

✅ Use natural language to interact with DataStage  
✅ Dynamically list and select projects without hardcoding IDs  
✅ Automate complex workflows without writing scripts  
✅ Chain multiple operations together intelligently  
✅ Access DataStage capabilities directly from your IDE  
✅ Convert DataStage flows to Python SDK code  

### What You've Learned

- How to extract API specifications from documentation
- How to craft effective prompts for Bob to generate Python code
- How Bob architectures production-ready MCP servers with Python
- Understanding Python project structure (`__init__.py`, `__pycache__`, etc.)
- How to use Python virtual environments and package management
- How async/await works in Python for efficient I/O
- How to implement dynamic project selection with priority systems
- How to securely configure and deploy Python MCP servers
- How to test and troubleshoot MCP integrations

### The Power of AI-Assisted Development

The most remarkable part of this tutorial is what you *didn't* have to do:

❌ You didn't write authentication logic  
❌ You didn't implement retry mechanisms  
❌ You didn't design the caching layer  
❌ You didn't create type hints and documentation  
❌ You didn't handle error cases  
❌ You didn't implement the project selection system  
❌ You didn't set up the Python package structure  

Bob analyzed your requirements, understood the API structure, and made intelligent architectural decisions to create a robust, maintainable system. You went from zero to a production-ready MCP server by simply describing what you wanted.

### Next Steps

Now that you have a working DataStage MCP server, consider:

1. **Adding more tools:** Extract more cURL commands and ask Bob to add new capabilities
   - Data quality rules management
   - Connection management
   - Environment variable management
   - Job scheduling

2. **Customizing behavior:** Ask Bob to modify:
   - Retry logic parameters
   - Caching duration
   - Error handling strategies
   - Logging levels

3. **Enhancing project management:**
   - Add project creation/deletion tools
   - Implement project metadata updates
   - Add project member management

4. **Creating templates:** Ask Bob to add tools for:
   - Creating reusable flow templates
   - Bulk operations across multiple projects
   - Flow comparison and diff tools

5. **Sharing your work:**
   - Package your MCP server as a Python package
   - Create a Docker container for easy deployment
   - Share on GitHub for others to use

6. **Building other integrations:**
   - Use the same approach for other IBM Cloud services
   - Create MCP servers for any REST API
   - Combine multiple MCP servers for complex workflows

7. **Advanced Python features:**
   - Add unit tests with pytest
   - Implement async context managers
   - Use Python decorators for cross-cutting concerns
   - Add type checking with mypy

The same principles you learned here can be applied to build MCP servers for any REST API, opening up endless possibilities for AI-powered automation.

Happy building! 🚀

---

## Appendix: Python vs TypeScript Comparison

For those familiar with the TypeScript version, here's a quick comparison:

| Aspect | TypeScript | Python |
|--------|-----------|--------|
| **Framework** | @modelcontextprotocol/sdk | FastMCP |
| **HTTP Client** | axios | httpx |
| **Async Pattern** | Promises | async/await |
| **Type System** | TypeScript types | Type hints (optional) |
| **Package Manager** | npm | pip |
| **Config File** | package.json | requirements.txt / pyproject.toml |
| **Build Step** | Required (tsc) | Not required (interpreted) |
| **Entry Point** | build/index.js | run_server.py |
| **Module System** | ES6 imports | Python imports |
| **Package Marker** | Not needed | `__init__.py` files |

Both implementations provide the same functionality—choose based on your team's expertise and preferences!
