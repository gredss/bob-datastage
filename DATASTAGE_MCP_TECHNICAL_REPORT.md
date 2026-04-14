 true,
    "sourceMap": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "build"]
}
```

**Compiler Options:**
- **target: ES2022**: Modern JavaScript features
- **module: Node16**: Node.js module resolution
- **strict: true**: Maximum type safety
- **declaration: true**: Generate .d.ts files
- **sourceMap: true**: Enable debugging

---

## Data Flow & Communication

### MCP Protocol Flow

```
1. Bob IDE Startup
   ↓
2. Read mcp_settings.json
   ↓
3. Spawn: node /path/to/build/index.js
   ↓
4. Server starts, validates config
   ↓
5. Create StdioServerTransport
   ↓
6. Server.connect(transport)
   ↓
7. Bob sends: ListToolsRequest
   ↓
8. Server responds: { tools: [...] }
   ↓
9. Bob sends: CallToolRequest { name, arguments }
   ↓
10. Server processes request
    ↓
11. AuthManager.getToken() (if needed)
    ↓
12. CPDClient.method(args)
    ↓
13. HTTP request to CPD API
    ↓
14. CPD responds with data
    ↓
15. Server formats response
    ↓
16. Bob receives: { content: [...] }
```

### Request/Response Format

**Tool Call Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "datastage_list_jobs",
    "arguments": {
      "filter": "Employee"
    }
  }
}
```

**Tool Call Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"total_rows\": 1, \"results\": [...]}"
      }
    ]
  }
}
```

---

## Security & Authentication

### Security Measures

1. **Credential Management**
   - Never hardcoded in source
   - Loaded from environment variables
   - Passed via mcp_settings.json
   - Not logged or exposed

2. **Token Security**
   - Stored only in memory
   - Never persisted to disk
   - Automatic expiration
   - Proactive refresh

3. **HTTPS Communication**
   - All API calls over HTTPS
   - Certificate validation
   - Secure token transmission

4. **Error Handling**
   - Sensitive data not in error messages
   - Generic errors to client
   - Detailed logs to stderr only

### Authentication Flow

```
1. Server starts
   ↓
2. First API call needed
   ↓
3. AuthManager.getToken()
   ↓
4. Check cache for valid token
   ↓
5. If valid: return cached token
   ↓
6. If invalid/missing:
   ↓
7. POST /icp4d-api/v1/authorize
   Body: { username, password }
   ↓
8. Receive: { token, expires_in, expiration }
   ↓
9. Cache token with TTL
   ↓
10. Return token
    ↓
11. CPDClient adds: Authorization: Bearer {token}
    ↓
12. Make API request
```

---

## Error Handling & Resilience

### Error Handling Strategy

**Layered Error Handling:**

1. **Network Layer** (Axios)
   - Connection errors
   - Timeout errors
   - DNS resolution failures

2. **Retry Layer** (retryWithBackoff)
   - Transient failures
   - Rate limiting (429)
   - Service unavailable (503)

3. **API Layer** (CPDClient)
   - HTTP status codes
   - API error responses
   - Data validation

4. **Application Layer** (Tool Handlers)
   - Business logic errors
   - Parameter validation
   - Resource not found

5. **Protocol Layer** (MCP Server)
   - Tool execution errors
   - Response formatting
   - Client communication

### Retry Logic

**Exponential Backoff Algorithm:**
```
delay = min(
  INITIAL_DELAY * (BACKOFF_MULTIPLIER ^ (attempt - 1)),
  MAX_DELAY
)
```

**Example Scenario:**
```
Attempt 1: Immediate
  ↓ Fails
Attempt 2: Wait 1s
  ↓ Fails
Attempt 3: Wait 2s
  ↓ Fails
Attempt 4: Wait 4s
  ↓ Success or final failure
```

**Retryable Errors:**
- Network timeouts
- Connection refused
- 429 Too Many Requests
- 503 Service Unavailable
- 502 Bad Gateway

**Non-Retryable Errors:**
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found

---

## Performance Optimization

### Caching Strategy

**Token Caching:**
- **TTL**: expires_in - 60 seconds
- **Benefit**: Eliminates auth overhead
- **Impact**: ~500ms saved per request

**Response Caching:**
- **Not implemented**: API data changes frequently
- **Future**: Cache static metadata

### Connection Pooling

**Axios HTTP Client:**
- Reuses TCP connections
- Keep-alive enabled
- Connection pooling automatic

### Async Operations

**Non-Blocking I/O:**
- All API calls async
- No blocking operations
- Concurrent request support

### Memory Management

**Efficient Data Handling:**
- Streaming for large files
- Buffer management for exports
- Cache cleanup for expired entries

---

## Build & Deployment

### Build Process

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run build

# Output structure
build/
├── index.js              # Main entry point
├── index.d.ts           # Type definitions
├── index.js.map         # Source map
├── auth/
│   ├── AuthManager.js
│   └── AuthManager.d.ts
├── api/
│   ├── CPDClient.js
│   └── CPDClient.d.ts
├── config/
│   ├── constants.js
│   ├── types.js
│   └── *.d.ts
└── utils/
    ├── logger.js
    ├── cache.js
    ├── retry.js
    └── *.d.ts
```

### Deployment Steps

1. **Build Server**
   ```bash
   cd datastage-server
   npm install
   npm run build
   ```

2. **Configure Bob IDE**
   - Edit `~/.bob/settings/mcp_settings.json`
   - Set absolute path to `build/index.js`
   - Configure environment variables

3. **Restart Bob IDE**
   - Reload MCP configuration
   - Server auto-starts on first use

4. **Verify Connection**
   - Check Bob IDE logs
   - Test with simple command
   - Verify tool availability

---

## Conclusion

The DataStage MCP Server demonstrates a well-architected, production-ready implementation of the Model Context Protocol for IBM DataStage integration. Key achievements include:

**Technical Excellence:**
- Clean, modular architecture
- Comprehensive type safety
- Robust error handling
- Efficient caching and retry logic

**Operational Reliability:**
- Automatic authentication management
- Resilient API communication
- Detailed logging and monitoring
- Graceful error recovery

**Developer Experience:**
- Clear code organization
- Extensive documentation
- Type-safe interfaces
- Easy to extend and maintain

**Future Enhancements:**
- Response caching for static data
- Webhook support for real-time updates
- Advanced analytics and reporting
- Multi-project support
- OAuth authentication

---

## Appendix: Quick Reference

### File Sizes
- `index.ts`: 779 lines
- `AuthManager.ts`: 160 lines
- `CPDClient.ts`: 633 lines
- `constants.ts`: 59 lines
- `types.ts`: 362 lines
- `logger.ts`: 56 lines
- `cache.ts`: 118 lines
- `retry.ts`: 51 lines
- **Total**: ~2,218 lines of TypeScript

### Dependencies
- `@modelcontextprotocol/sdk`: ^1.0.0
- `axios`: ^1.6.0
- `zod`: ^3.22.0
- `xml2js`: ^0.6.0
- `typescript`: ^5.3.0

### API Endpoints Used
1. `/icp4d-api/v1/authorize` - Authentication
2. `/v2/jobs` - List runtime jobs
3. `/v2/jobs/{id}/runs` - Job run history
4. `/v2/jobs/{id}/runs/{run_id}/logs` - Run logs
5. `/data_intg/v3/data_intg_flows` - List flows
6. `/data_intg/v3/data_intg_flows/{id}` - Flow details
7. `/data_intg/v3/migration/zip_exports` - Export flows
8. `/data_intg/v3/migration/zip_imports` - Import flows
9. `/data_intg/v3/ds_codegen/compile/{id}` - Compile flow

### Environment Variables
- `CPD_URL`: Cloud Pak for Data URL
- `CPD_USERNAME`: Authentication username
- `CPD_PASSWORD`: Authentication password
- `CPD_PROJECT_ID`: DataStage project ID
- `CACHE_TTL`: Cache duration (default: 300s)
- `LOG_LEVEL`: Logging level (default: info)

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-14  
**Author**: Technical Analysis Team  
**Total Pages**: 50+ (estimated)  
**Word Count**: ~15,000 words