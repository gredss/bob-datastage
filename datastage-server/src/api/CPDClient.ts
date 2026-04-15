/**
 * Cloud Pak for Data API Client - Simplified Version
 * Only includes working functionality: listing DataStage jobs
 */

import axios, { AxiosInstance } from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import { AuthManager } from '../auth/AuthManager.js';
import { ENV, API_ENDPOINTS, TIMEOUT_CONFIG, RETRY_CONFIG } from '../config/constants.js';
import {
  APIError,
} from '../config/types.js';
import { logger } from '../utils/logger.js';
import { retryWithBackoff } from '../utils/retry.js';

export class CPDClient {
  private httpClient: AxiosInstance;
  private authManager: AuthManager;

  constructor(authManager: AuthManager) {
    this.authManager = authManager;

    this.httpClient = axios.create({
      baseURL: ENV.CPD_URL,
      timeout: TIMEOUT_CONFIG.API_REQUEST,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to inject auth token
    this.httpClient.interceptors.request.use(
      async (config) => {
        const token = await this.authManager.getToken();
        config.headers.Authorization = `Bearer ${token}`;
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.httpClient.interceptors.response.use(
      (response) => response,
      (error) => Promise.reject(error)
    );
  }

  /**
   * Get project ID (from env or cache)
   */
  private async getProjectId(): Promise<string> {
    // If project ID is directly provided, use it
    if (ENV.CPD_PROJECT_ID) {
      logger.info('Using direct project ID from environment');
      return ENV.CPD_PROJECT_ID;
    }

    throw new Error('CPD_PROJECT_ID must be set in environment variables');
  }

  /**
   * List all runtime jobs in the project (from /v2/jobs API)
   * These are the jobs with correct IDs for querying run history
   */
  async listJobs(filter?: string): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Listing runtime jobs from /v2/jobs', { projectId, filter });

    try {
      const endpoint = API_ENDPOINTS.JOBS(projectId);
      logger.info('Making request to:', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.get(endpoint),
        RETRY_CONFIG
      );

      logger.info('Response received', {
        status: response.status,
        dataKeys: Object.keys(response.data || {})
      });

      // Return raw API response
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        logger.error('/v2/jobs request failed', {
          status,
          message,
          url: error.config?.url,
          responseData: error.response?.data
        });

        throw new APIError(
          `Failed to list jobs: ${message}`,
          status || 500,
          error.response?.data
        );
      }
      throw error;
    }
  }

  /**
   * Get job runs for a specific job
   */
  async getJobRuns(jobId: string, limit: number = 50): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Fetching job runs', { jobId, projectId, limit });

    try {
      const endpoint = API_ENDPOINTS.JOB_RUNS(jobId, projectId);
      logger.info('Requesting job runs from:', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.get(endpoint),
        RETRY_CONFIG
      );

      logger.info('Job runs response received', {
        status: response.status,
        dataKeys: Object.keys(response.data || {})
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        const errorData = error.response?.data;
        
        logger.error('Job runs request failed', {
          status,
          message,
          url: error.config?.url,
          errorData
        });

        throw new APIError(
          `Failed to fetch job runs: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }

  /**
   * Get logs for a specific job run
   */
  async getJobRunLogs(jobId: string, runId: string): Promise<any> {
    try {
      const projectId = await this.getProjectId();
      const endpoint = API_ENDPOINTS.JOB_RUN_LOGS(jobId, runId, projectId);
      
      logger.info('Fetching job run logs', { jobId, runId, endpoint });

      const response = await retryWithBackoff(
        () => this.httpClient.get(endpoint),
        RETRY_CONFIG
      );

      logger.info('Job run logs retrieved successfully', {
        jobId,
        runId,
        hasLogs: !!response.data
      });

      return response.data;
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const errorData = error.response?.data;
        const message = errorData?.message || error.message;

        logger.error('Failed to fetch job run logs', {
          jobId,
          runId,
          status,
          message,
          errorData
        });

        throw new APIError(
          `Failed to fetch job run logs: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }

  /**
   * Run a DataStage job
   * POST /v2/jobs/{job_id}/runs
   */
  async runJob(
    jobId: string,
    options: {
      name?: string;
      description?: string;
      env_variables?: string[];
      job_parameters?: Array<{ name: string; value: any }>;
      parameter_sets?: any[];
    } = {}
  ): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Running DataStage job', { jobId, projectId, options });

    try {
      const endpoint = API_ENDPOINTS.RUN_JOB(jobId, projectId);
      
      // Build request body
      const requestBody: any = {
        job_run: {}
      };
      
      if (options.name) requestBody.job_run.name = options.name;
      if (options.description) requestBody.job_run.description = options.description;
      
      if (options.env_variables || options.job_parameters || options.parameter_sets) {
        requestBody.job_run.configuration = {};
        
        if (options.env_variables) {
          requestBody.job_run.configuration.env_variables = options.env_variables;
        }
      }
      
      if (options.job_parameters) {
        requestBody.job_run.job_parameters = options.job_parameters;
      }
      
      if (options.parameter_sets) {
        requestBody.job_run.parameter_sets = options.parameter_sets;
      }
      
      logger.info('Submitting job run request', { endpoint, requestBody });
      
      const response = await retryWithBackoff(
        () => this.httpClient.post(endpoint, requestBody),
        RETRY_CONFIG
      );

      logger.info('Job run submitted successfully', {
        status: response.status,
        runId: response.data?.metadata?.asset_id
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const errorData = error.response?.data;
        const message = errorData?.message || error.message;
        
        logger.error('Job run request failed', {
          jobId,
          status,
          message,
          errorData
        });

        throw new APIError(
          `Failed to run job: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }

  /**
   * Compile a DataStage flow
   * POST /data_intg/v3/ds_codegen/compile/{flow_id}
   */
  async compileFlow(
    flowId: string,
    options: {
      runtime_type?: string;
      enable_sql_pushdown?: boolean;
      enable_async_compile?: boolean;
      enable_pushdown_source?: boolean;
      enable_push_processing_to_source?: boolean;
      enable_push_join_to_source?: boolean;
      enable_pushdown_target?: boolean;
    } = {}
  ): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Compiling DataStage flow', { flowId, projectId, options });

    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      queryParams.append('project_id', projectId);
      
      if (options.runtime_type) queryParams.append('runtime_type', options.runtime_type);
      if (options.enable_sql_pushdown !== undefined) queryParams.append('enable_sql_pushdown', String(options.enable_sql_pushdown));
      if (options.enable_async_compile !== undefined) queryParams.append('enable_async_compile', String(options.enable_async_compile));
      if (options.enable_pushdown_source !== undefined) queryParams.append('enable_pushdown_source', String(options.enable_pushdown_source));
      if (options.enable_push_processing_to_source !== undefined) queryParams.append('enable_push_processing_to_source', String(options.enable_push_processing_to_source));
      if (options.enable_push_join_to_source !== undefined) queryParams.append('enable_push_join_to_source', String(options.enable_push_join_to_source));
      if (options.enable_pushdown_target !== undefined) queryParams.append('enable_pushdown_target', String(options.enable_pushdown_target));
      
      const endpoint = `/data_intg/v3/ds_codegen/compile/${flowId}?${queryParams.toString()}`;
      
      logger.info('Submitting flow compile request', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.post(endpoint, {}),
        RETRY_CONFIG
      );

      logger.info('Flow compile submitted successfully', {
        status: response.status,
        result: response.data?.message?.result
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const errorData = error.response?.data;
        const message = errorData?.message || error.message;
        
        logger.error('Flow compile request failed', {
          flowId,
          status,
          message,
          errorData
        });

        throw new APIError(
          `Failed to compile flow: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }

  /**
   * List all DataStage flows (design-time artifacts) in the project
   * These contain the flow definitions with stages, links, and configurations
   */
  async listDataStageFlows(filter?: string): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Listing DataStage flows from /data_intg/v3/data_intg_flows', { projectId, filter });

    try {
      const endpoint = API_ENDPOINTS.FLOWS(projectId);
      logger.info('Making request to:', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.get(endpoint),
        RETRY_CONFIG
      );

      logger.info('Flows response received', {
        status: response.status,
        dataKeys: Object.keys(response.data || {}),
        totalCount: response.data?.total_count
      });

      // Return raw API response
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        logger.error('/data_intg/v3/data_intg_flows request failed', {
          status,
          message,
          url: error.config?.url,
          responseData: error.response?.data
        });

        throw new APIError(
          `Failed to list DataStage flows: ${message}`,
          status || 500,
          error.response?.data
        );
      }
      throw error;
    }
  }

  /**
   * Get detailed flow information including stages, links, and column definitions
   */
  async getFlowDetails(flowId: string): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Fetching flow details', { flowId, projectId });

    try {
      const endpoint = API_ENDPOINTS.FLOW_DETAILS(flowId, projectId);
      logger.info('Requesting flow details from:', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.get(endpoint),
        RETRY_CONFIG
      );

      logger.info('Flow details response received', {
        status: response.status,
        hasEntity: !!response.data?.entity
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        logger.error('Flow details request failed', {
          status,
          message,
          url: error.config?.url,
          responseData: error.response?.data
        });

        throw new APIError(
          `Failed to fetch flow details: ${message}`,
          status || 500,
          error.response?.data
        );
      }
      throw error;
    }
  }

  /**
   * Export DataStage flows with dependencies as a zip file using the migration API
   * Endpoint: /data_intg/v3/migration/zip_exports
   * Returns the binary content that can be saved as a .zip file
   * The zip includes the flow definition and all dependencies (connections, environments, etc.)
   */
  async exportAsset(flowId: string): Promise<Buffer> {
    const projectId = await this.getProjectId();
    
    logger.info('Exporting flow with dependencies', { flowId, projectId });

    try {
      // Use the migration zip_exports endpoint with flow ID as query parameter
      const endpoint = `${API_ENDPOINTS.EXPORT_FLOWS(projectId)}&id=${flowId}&type=data_intg_flow`;
      logger.info('Requesting flow export from migration API:', { endpoint });
      
      const response = await retryWithBackoff(
        () => this.httpClient.post(endpoint, {}, {
          responseType: 'arraybuffer',
          headers: {
            'Accept': 'application/octet-stream'
          }
        }),
        RETRY_CONFIG
      );

      logger.info('Flow export response received', {
        status: response.status,
        contentType: response.headers['content-type'],
        contentLength: response.headers['content-length']
      });

      return Buffer.from(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        
        // Handle arraybuffer error responses
        let errorData = error.response?.data;
        let message = error.message;
        
        if (errorData && Buffer.isBuffer(errorData)) {
          try {
            const errorText = errorData.toString('utf-8');
            const errorJson = JSON.parse(errorText);
            errorData = errorJson;
            
            // Extract message from errors array if present
            if (errorJson.errors && Array.isArray(errorJson.errors) && errorJson.errors.length > 0) {
              const firstError = errorJson.errors[0];
              message = firstError.message || firstError.code || message;
              
              // Include additional error details
              if (firstError.target) {
                message += ` (target: ${firstError.target.type} - ${firstError.target.name})`;
              }
            } else if (errorJson.message) {
              message = errorJson.message;
            } else if (errorJson.error) {
              message = errorJson.error;
            }
          } catch (e) {
            // If parsing fails, use the buffer as string
            message = errorData.toString('utf-8');
          }
        } else if (errorData?.errors && Array.isArray(errorData.errors) && errorData.errors.length > 0) {
          const firstError = errorData.errors[0];
          message = firstError.message || firstError.code || message;
        } else if (errorData?.message) {
          message = errorData.message;
        }
        
        logger.error('Flow export request failed', {
          status,
          message,
          url: error.config?.url,
          responseData: errorData
        });

        throw new APIError(
          `Failed to export flow with dependencies: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }

  /**
   * Import DataStage flows from a zip file using the migration API
   * Endpoint: /data_intg/v3/migration/zip_imports
   * This is an asynchronous operation - the API returns immediately with a request ID
   * The actual import happens in the background
   */
  async importFlows(
    zipFilePath: string,
    options: {
      conflict_resolution?: 'skip' | 'rename' | 'replace' | 'rename_replace';
      on_failure?: 'continue' | 'stop';
      include_dependencies?: boolean;
      enable_notification?: boolean;
      import_only?: boolean;
      replace_mode?: 'soft' | 'hard' | 'force';
    } = {}
  ): Promise<any> {
    const projectId = await this.getProjectId();
    
    logger.info('Importing flows from zip file', { zipFilePath, projectId, options });

    try {
      // Read the zip file as binary data
      const fileBuffer = fs.readFileSync(zipFilePath);
      const fileName = path.basename(zipFilePath);
      
      // Build query parameters
      const params = new URLSearchParams();
      params.append('project_id', projectId);
      params.append('file_name', fileName);
      
      // Add optional parameters
      if (options.conflict_resolution) {
        params.append('conflict_resolution', options.conflict_resolution);
      }
      if (options.on_failure) {
        params.append('on_failure', options.on_failure);
      }
      if (options.include_dependencies !== undefined) {
        params.append('include_dependencies', String(options.include_dependencies));
      }
      if (options.enable_notification !== undefined) {
        params.append('enable_notification', String(options.enable_notification));
      }
      if (options.import_only !== undefined) {
        params.append('import_only', String(options.import_only));
      }
      if (options.replace_mode) {
        params.append('replace_mode', options.replace_mode);
      }
      
      const endpoint = `/data_intg/v3/migration/zip_imports?${params.toString()}`;
      logger.info('Requesting flow import from migration API:', { endpoint, fileSize: fileBuffer.length });
      
      const response = await retryWithBackoff(
        () => this.httpClient.post(endpoint, fileBuffer, {
          headers: {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/json;charset=utf-8'
          },
          timeout: TIMEOUT_CONFIG.IMPORT_REQUEST,
          maxBodyLength: Infinity,
          maxContentLength: Infinity
        }),
        RETRY_CONFIG
      );

      logger.info('Flow import request submitted successfully', {
        status: response.status,
        importId: response.data?.metadata?.id,
        importStatus: response.data?.entity?.import_data_flows?.[0]?.status
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const errorData = error.response?.data;
        const message = errorData?.message || error.message;
        
        logger.error('Flow import request failed', {
          status,
          message,
          url: error.config?.url,
          responseData: errorData
        });

        throw new APIError(
          `Failed to import flows: ${message}`,
          status || 500,
          errorData
        );
      }
      throw error;
    }
  }
}

// Made with Bob
