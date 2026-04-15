/**
 * Configuration constants for DataStage MCP Server - Simplified Version
 */

// Environment variables
export const ENV = {
  CPD_URL: process.env.CPD_URL || '',
  CPD_USERNAME: process.env.CPD_USERNAME || '',
  CPD_PASSWORD: process.env.CPD_PASSWORD || '',
  CPD_PROJECT_ID: process.env.CPD_PROJECT_ID || '',
  CACHE_TTL: parseInt(process.env.CACHE_TTL || '300', 10), // 5 minutes default
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
} as const;

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTHORIZE: '/icp4d-api/v1/authorize',
  
  // Jobs API - v2 (Runtime jobs with correct IDs for runs)
  JOBS: (projectId: string) => `/v2/jobs?project_id=${projectId}`,
  JOB_RUNS: (jobId: string, projectId: string) => `/v2/jobs/${jobId}/runs?project_id=${projectId}`,
  RUN_JOB: (jobId: string, projectId: string) => `/v2/jobs/${jobId}/runs?project_id=${projectId}&userfs=false`,
  JOB_RUN_LOGS: (jobId: string, runId: string, projectId: string) => `/v2/jobs/${jobId}/runs/${runId}/logs?project_id=${projectId}&userfs=false`,
  
  // DataStage Flows (Jobs) - v3 API (Design-time, different IDs)
  FLOWS: (projectId: string) => `/data_intg/v3/data_intg_flows?project_id=${projectId}`,
  FLOW_DETAILS: (flowId: string, projectId: string) => `/data_intg/v3/data_intg_flows/${flowId}?project_id=${projectId}`,
  
  // Flow Export/Import (using migration API)
  EXPORT_FLOWS: (projectId: string) => `/data_intg/v3/migration/zip_exports?project_id=${projectId}`,
  IMPORT_FLOWS: (projectId: string) => `/data_intg/v3/migration/zip_imports?project_id=${projectId}`,
  
  // Flow Compilation
  COMPILE_FLOW: (flowId: string, projectId: string) => `/data_intg/v3/ds_codegen/compile/${flowId}?project_id=${projectId}`,
} as const;

// Cache keys
export const CACHE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  PROJECT_ID: 'project_id',
} as const;

// Retry configuration
export const RETRY_CONFIG = {
  MAX_RETRIES: 3,
  INITIAL_DELAY: 1000, // 1 second
  MAX_DELAY: 10000, // 10 seconds
  BACKOFF_MULTIPLIER: 2,
} as const;

// Timeout configuration
export const TIMEOUT_CONFIG = {
  API_REQUEST: 30000, // 30 seconds
  AUTH_REQUEST: 10000, // 10 seconds
  IMPORT_REQUEST: 120000, // 120 seconds (2 minutes) for import operations
} as const;

// Made with Bob
