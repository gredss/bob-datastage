/**
 * Type definitions for DataStage MCP Server
 */

// Job types
export interface Job {
  id: string;
  name: string;
  description?: string;
  project_id: string;
  asset_type: string;
  created_at: string;
  updated_at: string;
  last_run_status?: string;
  last_run_time?: string;
}

export interface JobRun {
  id: string;
  job_id: string;
  job_name: string;
  status: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  rows_read?: number;
  rows_written?: number;
  rows_rejected?: number;
  error_message?: string;
  warning_count?: number;
}

export interface JobRunDetails extends JobRun {
  stages: StageInfo[];
  parameters: Record<string, string>;
  environment: Record<string, string>;
}

export interface StageInfo {
  name: string;
  type: string;
  status: string;
  rows_input?: number;
  rows_output?: number;
  rows_rejected?: number;
  duration?: number;
  error_message?: string;
}

// Job design types
export interface JobDesign {
  id: string;
  name: string;
  description?: string;
  stages: Stage[];
  links: Link[];
  parameters: Parameter[];
  metadata: JobMetadata;
}

export interface Stage {
  name: string;
  type: string;
  properties: Record<string, any>;
  inputs: string[];
  outputs: string[];
  transformations?: Transformation[];
  constraints?: Constraint[];
}

export interface Link {
  name: string;
  from_stage: string;
  to_stage: string;
  type: 'data' | 'reject' | 'reference';
  columns: Column[];
}

export interface Column {
  name: string;
  type: string;
  nullable: boolean;
  length?: number;
  precision?: number;
  scale?: number;
}

export interface Transformation {
  column: string;
  expression: string;
  type: string;
}

export interface Constraint {
  name: string;
  expression: string;
  action: 'drop' | 'reject' | 'continue';
}

export interface Parameter {
  name: string;
  type: string;
  default_value?: string;
  prompt?: string;
  required: boolean;
}

export interface JobMetadata {
  version: string;
  created_by: string;
  created_at: string;
  modified_by: string;
  modified_at: string;
}

// Log parsing types
export interface ParsedLog {
  job_name: string;
  run_id: string;
  start_time: string;
  end_time?: string;
  status: string;
  errors: ErrorInfo[];
  warnings: WarningInfo[];
  stages: StageLog[];
  metrics: LogMetrics;
}

export interface ErrorInfo {
  timestamp: string;
  stage?: string;
  code: string;
  message: string;
  severity: 'fatal' | 'error' | 'warning';
  line_number?: number;
}

export interface WarningInfo {
  timestamp: string;
  stage?: string;
  message: string;
  line_number?: number;
}

export interface StageLog {
  name: string;
  type: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  rows_input: number;
  rows_output: number;
  rows_rejected: number;
  status: string;
}

export interface LogMetrics {
  total_rows_read: number;
  total_rows_written: number;
  total_rows_rejected: number;
  total_duration: number;
  throughput: number; // rows per second
  peak_memory?: number;
}

// Analysis types
export interface RootCause {
  category: string;
  description: string;
  affected_stage?: string;
  error_code?: string;
  confidence: number; // 0-1
  evidence: string[];
  recommendations: Recommendation[];
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
  impact: string;
  steps: string[];
}

export interface PerformanceIssue {
  type: 'bottleneck' | 'degradation' | 'inefficiency';
  description: string;
  affected_component: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  metrics: {
    current: number;
    baseline?: number;
    threshold?: number;
  };
  recommendations: Recommendation[];
}

export interface DesignIssue {
  type: 'anti_pattern' | 'missing_feature' | 'inefficiency' | 'best_practice';
  description: string;
  location: string; // stage or link name
  severity: 'critical' | 'high' | 'medium' | 'low';
  fix_available: boolean;
  recommendation: Recommendation;
}

// Fix types
export interface Fix {
  id: string;
  job_id: string;
  job_name: string;
  issue_type: string;
  description: string;
  changes: DesignChange[];
  validation_status: 'pending' | 'valid' | 'invalid';
  validation_errors?: string[];
  backup_created: boolean;
  backup_path?: string;
}

export interface DesignChange {
  type: 'add' | 'modify' | 'remove';
  target: 'stage' | 'link' | 'parameter' | 'transformation' | 'constraint';
  path: string; // e.g., "stages.Transformer_1.properties.cache_size"
  old_value?: any;
  new_value?: any;
  reason: string;
}

// Report types
export interface Report {
  id: string;
  type: string;
  format: string;
  generated_at: string;
  time_range: {
    start: string;
    end: string;
  };
  summary: ReportSummary;
  sections: ReportSection[];
  data?: any; // Raw data for JSON format
}

export interface ReportSummary {
  total_jobs: number;
  total_runs: number;
  success_rate: number;
  average_duration: number;
  total_rows_processed: number;
  key_findings: string[];
}

export interface ReportSection {
  title: string;
  type: 'text' | 'table' | 'chart' | 'list';
  content: any;
}

// Metrics types
export interface AggregatedMetrics {
  metric_type: string;
  time_range: {
    start: string;
    end: string;
  };
  group_by?: string;
  data: MetricDataPoint[];
}

export interface MetricDataPoint {
  timestamp?: string;
  label: string;
  value: number;
  unit?: string;
  metadata?: Record<string, any>;
}

// API response types
export interface CPDAuthResponse {
  token: string;
  token_type: string;
  expires_in: number;
  expiration: number;
}

export interface CPDProject {
  metadata: {
    guid: string;
    name: string;
    description?: string;
    created_at: string;
  };
  entity: {
    name: string;
    description?: string;
  };
}

export interface CPDJobsResponse {
  total_count: number;
  results: Job[];
}

export interface CPDJobRunsResponse {
  total_count: number;
  runs: JobRun[];
}

// Cache types
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

// Error types
export class DataStageError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'DataStageError';
  }
}

export class AuthenticationError extends DataStageError {
  constructor(message: string, details?: any) {
    super(message, 'AUTH_ERROR', 401, details);
    this.name = 'AuthenticationError';
  }
}

export class APIError extends DataStageError {
  constructor(message: string, statusCode: number, details?: any) {
    super(message, 'API_ERROR', statusCode, details);
    this.name = 'APIError';
  }
}

export class ValidationError extends DataStageError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', 400, details);
    this.name = 'ValidationError';
  }
}

// Utility types
export type JobStatus = 'success' | 'failed' | 'running' | 'aborted' | 'warning' | 'not_started';
export type ErrorCategory = 'data_quality' | 'design_flaw' | 'resource_constraint' | 'configuration' | 'environmental' | 'unknown';
export type ReportType = 'executive' | 'performance' | 'failure' | 'trend';
export type ReportFormat = 'excel' | 'pdf' | 'html' | 'json';
export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type Priority = 'high' | 'medium' | 'low';
export type Effort = 'low' | 'medium' | 'high';

// Made with Bob
