# DataStage MCP Server - Complete File Explanation

This document provides a comprehensive explanation of every file in the Python DataStage MCP server, detailing their purposes, how they work, why they exist, and how they were designed.

---

## Table of Contents

1. [Project Root Files](#project-root-files)
2. [Source Code Structure](#source-code-structure)
3. [Configuration Module](#configuration-module)
4. [Authentication Module](#authentication-module)
5. [API Module](#api-module)
6. [Utilities Module](#utilities-module)
7. [Main Server](#main-server)
8. [How Everything Works Together](#how-everything-works-together)

---

## Project Root Files

### `pyproject.toml`

**Purpose**: Modern Python project configuration file following PEP 518 standards.

**What it does**:
- Defines project metadata (name, version, description, author)
- Specifies Python version requirement (>=3.10)
- Lists core dependencies (fastmcp, httpx, pydantic, ibm-watsonx-data-integration)
- Defines optional development dependencies (pytest, black, ruff)
- Configures build system using hatchling
- Sets up entry point script (`datastage-server`)
- Configures code formatting tools (black, ruff)

**Why it exists**: 
- Replaces the older setup.py approach with a standardized configuration format
- Enables `pip install -e .` for development installation
- Provides a single source of truth for project configuration
- Makes the project pip-installable and distributable

**How it was made**:
- Follows modern Python packaging standards (PEP 517/518)
- Uses hatchling as the build backend for simplicity
- Includes both runtime and development dependencies
- Configures code quality tools with consistent settings

---

### `requirements.txt`

**Purpose**: Simple dependency list for pip installation.

**What it does**:
- Lists all required Python packages with minimum versions
- Core dependencies: fastmcp (MCP framework), httpx (HTTP client), pydantic (data validation)
- IBM SDK: ibm-watsonx-data-integration (for DataStage Python SDK code generation)

**Why it exists**:
- Provides a simple way to install dependencies: `pip install -r requirements.txt`
- More familiar to developers than pyproject.toml
- Useful for Docker containers and CI/CD pipelines
- Complements pyproject.toml for different installation scenarios

**How it was made**:
- Mirrors the dependencies from pyproject.toml
- Uses minimum version specifiers (>=) for flexibility
- Includes comments for clarity
- Organized by dependency type (core vs SDK)

---

### `README.md`

**Purpose**: Comprehensive documentation for the Python DataStage MCP server.

**What it does**:
- Explains what the server does and its features
- Provides installation instructions
- Documents configuration requirements (environment variables)
- Lists all available tools with examples
- Explains project structure
- Includes troubleshooting guide
- Compares with TypeScript version

**Why it exists**:
- First point of reference for users and developers
- Reduces support burden by answering common questions
- Provides quick-start guide for new users
- Documents API usage with practical examples

**How it was made**:
- Structured with clear sections and table of contents
- Includes code examples for each tool
- Provides both standalone and Bob IDE integration instructions
- Documents all configuration options
- Includes troubleshooting section based on common issues

---

## Source Code Structure

### `python/src/__init__.py`

**Purpose**: Package initialization file marking `src` as a Python package.

**What it does**:
- Defines package version (`__version__ = "0.1.0"`)
- Makes the directory importable as a Python module
- Provides package-level metadata

**Why it exists**:
- Required by Python to treat directory as a package
- Allows imports like `from src.server import main`
- Provides version information for the package
- Enables relative imports within the package

**How it was made**:
- Minimal implementation following Python conventions
- Includes version string for package management
- Contains "Made with Bob" signature

---

## Configuration Module

### `python/src/config/__init__.py`

**Purpose**: Configuration module initialization and exports.

**What it does**:
- Imports all configuration classes from constants.py
- Exports them via `__all__` for clean imports
- Makes configuration accessible as `from src.config import ENV`

**Why it exists**:
- Provides a clean public API for the configuration module
- Centralizes configuration exports
- Enables `from src.config import ENV, API_ENDPOINTS` instead of longer imports
- Follows Python best practices for package structure

**How it was made**:
- Imports all configuration classes
- Uses `__all__` to explicitly define public API
- Keeps imports organized and maintainable

---

### `python/src/config/constants.py`

**Purpose**: Central configuration file containing all constants, endpoints, and settings.

**What it does**:

1. **ENV Class**: Reads environment variables
   - `CPD_URL`: Cloud Pak for Data instance URL
   - `CPD_USERNAME`: Authentication username
   - `CPD_PASSWORD`: Authentication password
   - `CPD_PROJECT_ID`: Target project ID
   - `CACHE_TTL`: Cache time-to-live (default: 300 seconds)
   - `LOG_LEVEL`: Logging level (default: info)

2. **API_ENDPOINTS Class**: Defines all CPD API endpoints
   - Authentication: `/icp4d-api/v1/authorize`
   - Jobs API (v2): Runtime jobs, runs, logs
   - Flows API (v3): Design-time flows, details
   - Migration API: Export/import flows
   - Compilation API: Flow compilation

3. **CACHE_KEYS Class**: Cache key constants
   - `AUTH_TOKEN`: Key for cached authentication token
   - `PROJECT_ID`: Key for cached project ID

4. **RETRY_CONFIG Class**: Retry behavior configuration
   - `MAX_RETRIES`: 3 attempts
   - `INITIAL_DELAY`: 1 second
   - `MAX_DELAY`: 10 seconds
   - `BACKOFF_MULTIPLIER`: 2x exponential backoff

5. **TIMEOUT_CONFIG Class**: HTTP timeout settings
   - `API_REQUEST`: 30 seconds for normal requests
   - `AUTH_REQUEST`: 10 seconds for authentication
   - `IMPORT_REQUEST`: 120 seconds for import operations

**Why it exists**:
- Single source of truth for all configuration
- Environment-based configuration for different deployments
- Type-safe configuration using classes
- Easy to modify and maintain
- Prevents hardcoded values scattered throughout code

**How it was made**:
- Uses classes as namespaces for related constants
- Static methods for dynamic endpoint generation
- Reads from environment variables with sensible defaults
- Organized by functional area (auth, API, cache, retry, timeout)
- Uses type hints for clarity

**Design decisions**:
- Classes instead of dictionaries for better IDE support
- Static methods for endpoints that need parameters
- Separate timeout values for different operation types
- Conservative retry settings to avoid overwhelming the server

---

## Authentication Module

### `python/src/auth/__init__.py`

**Purpose**: Authentication module initialization and exports.

**What it does**:
- Imports AuthManager and AuthenticationError
- Exports them for use in other modules
- Provides clean import path: `from src.auth import AuthManager`

**Why it exists**:
- Encapsulates authentication functionality
- Provides clean public API
- Enables easy imports throughout the codebase

**How it was made**:
- Simple import/export pattern
- Uses `__all__` for explicit API definition

---

### `python/src/auth/auth_manager.py`

**Purpose**: Manages authentication with Cloud Pak for Data, including token generation, caching, and refresh.

**What it does**:

1. **Token Management**:
   - Generates bearer tokens via CPD authentication API
   - Caches tokens to avoid repeated authentication
   - Automatically refreshes expired tokens
   - Validates token expiration with 60-second buffer

2. **Authentication Flow**:
   - Checks cache for valid token
   - If not found or expired, authenticates with CPD
   - Stores token with TTL in cache
   - Returns valid token for API requests

3. **Error Handling**:
   - Custom `AuthenticationError` exception
   - Detailed error logging
   - Includes status codes and error details

**Key Methods**:

- `get_token()`: Main method to get a valid token (checks cache first)
- `_authenticate()`: Performs actual authentication with CPD
- `_build_auth_payload()`: Builds authentication request payload
- `_is_token_valid()`: Checks if cached token is still valid
- `refresh_token()`: Forces token refresh
- `clear_cache()`: Clears cached authentication data
- `validate_configuration()`: Validates required environment variables

**Why it exists**:
- Centralizes authentication logic
- Prevents repeated authentication calls (performance)
- Handles token expiration automatically
- Provides consistent error handling
- Separates authentication concerns from API logic

**How it was made**:

1. **Token Caching Strategy**:
   - Uses SimpleCache for in-memory storage
   - Calculates TTL from token expiration
   - Adds 60-second buffer to prevent edge cases
   - Minimum TTL of 60 seconds for safety

2. **Authentication Process**:
   - Uses httpx for async HTTP requests
   - Disables SSL verification (verify=False) for development
   - Posts to `/icp4d-api/v1/authorize` endpoint
   - Extracts token and expiration from response

3. **Error Handling**:
   - Catches HTTPStatusError for API errors
   - Logs detailed error information
   - Raises custom AuthenticationError with context
   - Includes original error details for debugging

**Design decisions**:
- Async/await for non-blocking operations
- Token expiration buffer prevents race conditions
- Cache-first approach reduces API calls
- Separate validation method for early error detection
- Username/password authentication (could be extended for API keys)

---

## API Module

### `python/src/api/__init__.py`

**Purpose**: API module initialization and exports.

**What it does**:
- Imports CPDClient and APIError
- Exports them for use throughout the application
- Provides clean import: `from src.api import CPDClient`

**Why it exists**:
- Encapsulates API client functionality
- Provides clean public API
- Enables organized imports

---

### `python/src/api/cpd_client.py`

**Purpose**: Cloud Pak for Data API client - the core interface for all DataStage operations.

**What it does**:

This is the most complex file in the project. It provides methods for:

1. **Job Operations** (Runtime - v2 API):
   - `list_jobs()`: List all runtime jobs
   - `get_job_runs()`: Get execution history for a job
   - `get_job_run_logs()`: Get logs for a specific run
   - `run_job()`: Execute a job with parameters

2. **Flow Operations** (Design-time - v3 API):
   - `list_datastage_flows()`: List all flow definitions
   - `get_flow_details()`: Get complete flow metadata
   - `compile_flow()`: Compile flow to generate runtime assets

3. **Import/Export Operations** (Migration API):
   - `export_asset()`: Export flow with dependencies as zip
   - `import_flows()`: Import flows from zip file

**Key Components**:

1. **APIError Class**:
   - Custom exception for API errors
   - Includes status code and error details
   - Provides structured error information

2. **CPDClient Class**:
   - Initialized with AuthManager for authentication
   - Stores base URL from environment
   - Provides all API methods

3. **Core Methods**:

   - `_get_project_id()`: Gets project ID from environment
   - `_make_request()`: Generic HTTP request method with authentication

**Why it exists**:
- Abstracts CPD API complexity
- Provides type-safe, async API methods
- Handles authentication automatically
- Implements retry logic for reliability
- Centralizes error handling
- Separates API concerns from business logic

**How it was made**:

1. **Request Handling**:
   - Uses httpx.AsyncClient for async HTTP
   - Automatically adds Bearer token to headers
   - Handles URL construction (base + endpoint)
   - Disables SSL verification for development
   - Configurable timeouts per operation type

2. **Retry Logic**:
   - Wraps requests in `retry_with_backoff()`
   - Handles transient failures automatically
   - Uses exponential backoff
   - Configurable retry parameters

3. **Error Handling**:
   - Catches HTTPStatusError for API errors
   - Logs detailed error information
   - Raises APIError with context
   - Includes request URL and response details

4. **API Method Patterns**:
   ```python
   async def method_name(self, params):
       # 1. Get project ID
       project_id = await self._get_project_id()
       
       # 2. Build endpoint
       endpoint = API_ENDPOINTS.METHOD(project_id)
       
       # 3. Make request with retry
       async def make_request():
           return await self._make_request('GET', endpoint)
       response = await retry_with_backoff(make_request)
       
       # 4. Parse and return response
       return response.json()
   ```

**Design decisions**:

- **Separate v2 and v3 APIs**: Jobs (runtime) vs Flows (design-time) use different APIs
- **Async throughout**: All methods are async for non-blocking I/O
- **Retry wrapper**: Separate retry logic for reusability
- **Structured logging**: Logs include context for debugging
- **Type hints**: All parameters and returns are typed
- **Error context**: Errors include original request details
- **Binary handling**: Special handling for zip file uploads/downloads

**Complex Operations Explained**:

1. **Export Flow**:
   - Uses migration API endpoint
   - Adds flow ID and type as query parameters
   - Sets Accept header to application/octet-stream
   - Returns raw bytes (zip file content)

2. **Import Flow**:
   - Reads zip file as binary
   - Builds complex query string with all parameters
   - Sets Content-Type to application/octet-stream
   - Uses longer timeout (120s) for large imports
   - Returns import metadata with status

3. **Run Job**:
   - Builds complex request body with job_run object
   - Supports environment variables, job parameters, parameter sets
   - Returns run ID and initial status
   - Job executes asynchronously on CPD

4. **Compile Flow**:
   - Builds query string with compilation options
   - Supports multiple runtime types (dspxosh, Spark)
   - Supports SQL pushdown options
   - Can compile synchronously or asynchronously

---

## Utilities Module

### `python/src/utils/__init__.py`

**Purpose**: Utilities module initialization and exports.

**What it does**:
- Imports logger, SimpleCache, and retry_with_backoff
- Exports them for use throughout the application
- Provides clean imports: `from src.utils import logger`

**Why it exists**:
- Encapsulates utility functionality
- Provides clean public API
- Enables organized imports

---

### `python/src/utils/logger.py`

**Purpose**: Simple, structured logging utility for the entire application.

**What it does**:

1. **Logger Class**:
   - Provides debug, info, warn, error methods
   - Formats messages with timestamp and level
   - Supports structured metadata (JSON)
   - Respects LOG_LEVEL environment variable

2. **Log Levels**:
   - debug: Detailed information for debugging
   - info: General informational messages
   - warn: Warning messages
   - error: Error messages

3. **Message Formatting**:
   - ISO 8601 timestamp with UTC timezone
   - Log level in uppercase
   - Message text
   - Optional metadata as JSON

**Why it exists**:
- Provides consistent logging across the application
- Structured logs are easier to parse and analyze
- Level-based filtering reduces noise
- Timestamps enable debugging timing issues
- Metadata provides context without cluttering messages

**How it was made**:

1. **Level Filtering**:
   - Compares message level to configured level
   - Only logs messages at or above configured level
   - Uses index-based comparison for efficiency

2. **Message Formatting**:
   - Uses datetime.utcnow() for consistent timestamps
   - Formats as ISO 8601 with 'Z' suffix
   - Includes level in brackets for easy filtering
   - Appends metadata as JSON if provided

3. **Output**:
   - Writes to stderr (standard for logs)
   - Allows stdout for actual program output
   - Compatible with log aggregation tools

**Design decisions**:
- Simple implementation (no external dependencies)
- Structured format (easy to parse)
- UTC timestamps (no timezone confusion)
- Stderr output (separates logs from data)
- Global instance (easy to import and use)

**Example output**:
```
[2026-04-30T05:32:00.000Z] [INFO] Authenticating with Cloud Pak for Data
[2026-04-30T05:32:01.234Z] [INFO] Successfully authenticated with CPD
[2026-04-30T05:32:02.456Z] [ERROR] Request failed {"error": "Connection timeout"}
```

---

### `python/src/utils/cache.py`

**Purpose**: Simple in-memory cache implementation with TTL (time-to-live) support.

**What it does**:

1. **CacheEntry Class**:
   - Stores data with timestamp and TTL
   - Tracks when entry was created
   - Knows when entry expires

2. **SimpleCache Class**:
   - Stores key-value pairs in memory
   - Automatically expires old entries
   - Provides get, set, delete, clear operations
   - Supports cache size and existence checks
   - Includes cleanup method for expired entries

**Key Methods**:

- `get(key)`: Retrieve value, returns None if expired/missing
- `set(key, data, ttl)`: Store value with TTL in seconds
- `delete(key)`: Remove specific entry
- `clear()`: Remove all entries
- `has(key)`: Check if key exists and is valid
- `size()`: Get number of cached entries
- `cleanup()`: Remove all expired entries

**Why it exists**:
- Reduces API calls by caching responses
- Improves performance (memory is faster than network)
- Prevents rate limiting issues
- Reduces load on CPD server
- Automatic expiration prevents stale data

**How it was made**:

1. **TTL Implementation**:
   - Stores timestamp when entry is created
   - Calculates expiration: timestamp + TTL
   - Checks expiration on every get/has operation
   - Automatically deletes expired entries

2. **Memory Management**:
   - Uses Python dictionary for storage
   - Lazy deletion (on access, not timer-based)
   - Cleanup method for manual garbage collection
   - No maximum size limit (could be added)

3. **Thread Safety**:
   - Not thread-safe (single-threaded async application)
   - Could be extended with locks if needed

**Design decisions**:
- In-memory only (no persistence needed)
- Lazy expiration (simpler, good enough)
- No size limits (small cache, controlled usage)
- Structured logging for debugging
- Simple API (easy to use)

**Usage pattern**:
```python
cache = SimpleCache()
cache.set('token', 'abc123', ttl=3600)  # Cache for 1 hour
token = cache.get('token')  # Returns 'abc123' if not expired
```

---

### `python/src/utils/retry.py`

**Purpose**: Retry utility with exponential backoff for handling transient failures.

**What it does**:

1. **Retry Logic**:
   - Attempts function execution
   - If it fails, waits and retries
   - Uses exponential backoff (delay doubles each time)
   - Caps maximum delay
   - Gives up after max retries

2. **Exponential Backoff**:
   - Attempt 1: 1 second delay
   - Attempt 2: 2 seconds delay
   - Attempt 3: 4 seconds delay
   - Maximum: 10 seconds delay

**Why it exists**:
- Handles transient network failures
- Prevents overwhelming failing services
- Improves reliability without manual intervention
- Standard pattern for distributed systems
- Reduces impact of temporary issues

**How it was made**:

1. **Recursive Implementation**:
   - Calls itself with incremented attempt counter
   - Base case: success or max retries exceeded
   - Recursive case: wait and try again

2. **Backoff Calculation**:
   ```python
   delay = min(
       initial_delay * (backoff_multiplier ** (attempt - 1)),
       max_delay
   )
   ```
   - Exponential growth: 1s, 2s, 4s, 8s, 10s (capped)
   - Prevents infinite delays

3. **Async Support**:
   - Uses `await asyncio.sleep()` for delays
   - Works with async functions
   - Non-blocking delays

**Design decisions**:
- Exponential backoff (standard practice)
- Configurable parameters (flexibility)
- Recursive implementation (clean code)
- Structured logging (debugging)
- Type hints (type safety)
- Async-first (matches application design)

**Usage pattern**:
```python
async def make_api_call():
    return await client.get('/api/endpoint')

# Automatically retries on failure
result = await retry_with_backoff(make_api_call)
```

---

## Main Server

### `python/src/server.py`

**Purpose**: Main FastMCP server file - the heart of the application that ties everything together.

**What it does**:

This is the entry point and orchestration layer. It:

1. **Initializes Components**:
   - Creates AuthManager instance
   - Creates CPDClient with AuthManager
   - Creates FastMCP server instance

2. **Defines MCP Tools** (10 tools total):
   - `datastage_list_jobs`: List runtime jobs
   - `datastage_get_job_runs`: Get job execution history
   - `datastage_get_job_run_logs`: Get run logs
   - `datastage_list_flows`: List flow definitions
   - `datastage_get_flow_details`: Get flow metadata
   - `datastage_export_flow`: Export flow as zip
   - `datastage_import_flow`: Import flow from zip
   - `datastage_run_job`: Execute a job
   - `datastage_compile_flow`: Compile flow
   - `datastage_convert_flow_to_python`: Convert flow to Python SDK code

3. **Provides Main Entry Point**:
   - Validates configuration
   - Starts FastMCP server
   - Handles server lifecycle

**Why it exists**:
- Entry point for the MCP server
- Defines the public API (tools)
- Orchestrates all components
- Handles tool invocations
- Provides user-facing interface

**How it was made**:

1. **FastMCP Integration**:
   ```python
   mcp = FastMCP("datastage-server")
   
   @mcp.tool()
   async def tool_name(param: str) -> str:
       # Tool implementation
       return json.dumps(result, indent=2)
   ```
   - Decorator-based tool registration
   - Automatic parameter validation
   - JSON string responses

2. **Tool Implementation Pattern**:
   ```python
   @mcp.tool()
   async def datastage_operation(params) -> str:
       # 1. Log operation
       logger.info('Operation starting', {'params': params})
       
       # 2. Call CPD client
       result = await cpd_client.method(params)
       
       # 3. Return JSON
       return json.dumps(result, indent=2)
   ```

3. **Error Handling**:
   - Try-catch blocks in tools
   - Returns error as JSON
   - Includes context in error response
   - Logs errors for debugging

4. **Configuration Validation**:
   - Checks required environment variables
   - Fails fast with clear error messages
   - Validates before starting server

**Tool Explanations**:

1. **datastage_list_jobs**:
   - Lists all runtime jobs in project
   - Uses v2 Jobs API
   - Optional filter parameter
   - Returns job metadata including IDs

2. **datastage_get_job_runs**:
   - Gets execution history for a job
   - Finds job by name first
   - Extracts job ID from response
   - Fetches runs using job ID
   - Returns run history with statuses

3. **datastage_get_job_run_logs**:
   - Gets logs for specific run
   - Requires both job_id and run_id
   - Returns detailed log entries
   - Useful for debugging failures

4. **datastage_list_flows**:
   - Lists design-time flow definitions
   - Uses v3 DataStage Flows API
   - Different IDs than runtime jobs
   - Returns flow metadata

5. **datastage_get_flow_details**:
   - Gets complete flow definition
   - Includes stages, links, columns
   - Shows transformations and logic
   - Useful for understanding flow design

6. **datastage_export_flow**:
   - Exports flow with dependencies
   - Creates zip file
   - Saves to workspace directory (from WORKSPACE_DIR env var)
   - Returns file path and size
   - Handles both absolute and relative paths

7. **datastage_import_flow**:
   - Imports flow from zip file
   - Resolves paths relative to workspace directory
   - Handles conflict resolution
   - Supports various import options
   - Asynchronous operation (returns import ID)

8. **datastage_run_job**:
   - Executes a DataStage job
   - Supports parameters and environment variables
   - Returns run ID for tracking
   - Job runs asynchronously on CPD

9. **datastage_compile_flow**:
   - Compiles flow to runtime assets
   - Required after flow modifications
   - Supports different runtime types
   - Can be synchronous or asynchronous

10. **datastage_convert_flow_to_python**:
    - Converts exported flow to Python SDK code
    - Uses IBM DataStage Python SDK
    - Resolves input/output paths relative to workspace directory
    - Generates Python code for flow recreation
    - Enables programmatic flow manipulation
    - Supports version control of flows

**Design decisions**:
- FastMCP for simplicity (vs standard MCP SDK)
- JSON string responses (MCP requirement)
- Async throughout (non-blocking I/O)
- Structured error responses
- Detailed logging for debugging
- Configuration validation at startup
- Tool names follow convention: `datastage_*`
- **Workspace directory handling**: Uses `WORKSPACE_DIR` environment variable to resolve relative paths to Bob's workspace, not the MCP server directory

**Main Function**:
```python
def main():
    # 1. Validate configuration
    if not ENV.CPD_URL:
        raise Exception('CPD_URL required')
    
    # 2. Log startup
    logger.info('Starting DataStage MCP Server')
    
    # 3. Run FastMCP server
    mcp.run()
```

---

## How Everything Works Together

### Application Flow

1. **Startup**:
   ```
   main() called
   ↓
   Validate environment variables
   ↓
   Initialize AuthManager
   ↓
   Initialize CPDClient with AuthManager
   ↓
   Create FastMCP server
   ↓
   Register tools with decorators
   ↓
   Start MCP server (mcp.run())
   ```

2. **Tool Invocation** (e.g., list jobs):
   ```
   Bob IDE calls datastage_list_jobs
   ↓
   server.py: datastage_list_jobs() function
   ↓
   cpd_client.list_jobs()
   ↓
   cpd_client._get_project_id() (from ENV)
   ↓
   cpd_client._make_request()
   ↓
   auth_manager.get_token()
   ↓
   Check cache for valid token
   ↓
   If not cached: auth_manager._authenticate()
   ↓
   POST to /icp4d-api/v1/authorize
   ↓
   Cache token with TTL
   ↓
   Return token
   ↓
   Add token to request headers
   ↓
   retry_with_backoff(request_function)
   ↓
   GET /v2/jobs?project_id=...
   ↓
   Parse JSON response
   ↓
   Return to server.py
   ↓
   Convert to JSON string
   ↓
   Return to Bob IDE
   ```

3. **Authentication Flow**:
   ```
   Need token for API call
   ↓
   auth_manager.get_token()
   ↓
   cache.get('auth_token')
   ↓
   If cached and valid: return token
   ↓
   If not: _authenticate()
   ↓
   Build auth payload (username/password)
   ↓
   POST to /icp4d-api/v1/authorize
   ↓
   Extract token and expiration
   ↓
   cache.set('auth_token', token, ttl)
   ↓
   Return token
   ```

4. **Error Handling Flow**:
   ```
   API request fails
   ↓
   HTTPStatusError raised
   ↓
   retry_with_backoff catches error
   ↓
   Log warning with attempt number
   ↓
   Wait with exponential backoff
   ↓
   Retry request
   ↓
   If max retries exceeded: raise error
   ↓
   CPDClient catches error
   ↓
   Log detailed error information
   ↓
   Raise APIError with context
   ↓
   Server tool catches error
   ↓
   Return error as JSON to Bob IDE
   ```

### Module Dependencies

```
server.py
├── auth/auth_manager.py
│   ├── config/constants.py
│   ├── utils/cache.py
│   └── utils/logger.py
├── api/cpd_client.py
│   ├── auth/auth_manager.py
│   ├── config/constants.py
│   ├── utils/logger.py
│   └── utils/retry.py
├── config/constants.py
└── utils/logger.py
```

### Data Flow

1. **Configuration** (constants.py):
   - Reads environment variables
   - Provides to all modules
   - Single source of truth

2. **Authentication** (auth_manager.py):
   - Manages tokens
   - Uses cache for performance
   - Provides tokens to API client

3. **API Client** (cpd_client.py):
   - Uses auth manager for tokens
   - Makes HTTP requests
   - Handles retries
   - Returns structured data

4. **Server** (server.py):
   - Receives tool calls from Bob IDE
   - Orchestrates API client calls
   - Returns JSON responses
   - Handles errors gracefully

### Key Design Patterns

1. **Dependency Injection**:
   - CPDClient receives AuthManager
   - Enables testing and flexibility

2. **Separation of Concerns**:
   - Auth logic in auth_manager
   - API logic in cpd_client
   - Tool definitions in server
   - Configuration in constants

3. **Async/Await**:
   - Non-blocking I/O throughout
   - Better performance
   - Handles concurrent requests

4. **Caching**:
   - Reduces API calls
   - Improves performance
   - Automatic expiration

5. **Retry with Backoff**:
   - Handles transient failures
   - Exponential backoff
   - Configurable behavior

6. **Structured Logging**:
   - Consistent format
   - Includes context
   - Easy to parse

7. **Error Handling**:
   - Custom exceptions
   - Detailed error context
   - Graceful degradation

### Why This Architecture?

1. **Modularity**: Each module has a single responsibility
2. **Testability**: Components can be tested independently
3. **Maintainability**: Clear structure, easy to modify
4. **Scalability**: Can add new tools easily
5. **Reliability**: Retry logic, caching, error handling
6. **Performance**: Async I/O, caching, connection pooling
7. **Debuggability**: Structured logging, detailed errors

---

## Summary

This Python DataStage MCP server is a well-architected application that:

- **Connects** Bob IDE to IBM DataStage via MCP protocol
- **Authenticates** with Cloud Pak for Data using bearer tokens
- **Provides** 10 tools for DataStage operations
- **Handles** errors gracefully with retries and detailed logging
- **Caches** authentication tokens for performance
- **Uses** modern Python patterns (async/await, type hints)
- **Follows** best practices (separation of concerns, DRY principle)

Every file has a specific purpose and works together to create a reliable, maintainable, and performant MCP server for DataStage integration.

---

**Made with Bob**