#!/usr/bin/env node

/**
 * DataStage MCP Server - Simplified Version
 * Provides Bob IDE with basic DataStage job listing capability
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { AuthManager } from './auth/AuthManager.js';
import { CPDClient } from './api/CPDClient.js';
import { logger } from './utils/logger.js';
import { ENV } from './config/constants.js';
import * as fs from 'fs';
import * as path from 'path';

// Initialize managers
const authManager = new AuthManager();
const cpdClient = new CPDClient(authManager);

// Create MCP server
const server = new Server(
  {
    name: 'datastage-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const tools: Tool[] = [
  {
    name: 'datastage_list_jobs',
    description: 'List all DataStage jobs in the configured project. Optionally filter by job name pattern.',
    inputSchema: {
      type: 'object',
      properties: {
        filter: {
          type: 'string',
          description: 'Optional filter pattern for job names',
        },
      },
    },
  },
  {
    name: 'datastage_get_job_runs',
    description: 'Get run history for a specific DataStage job using the /v2/jobs API.',
    inputSchema: {
      type: 'object',
      properties: {
        job_name: {
          type: 'string',
          description: 'Name of the DataStage job',
        },
        limit: {
          type: 'number',
          description: 'Maximum number of runs to return (default: 50)',
          default: 50,
        },
      },
      required: ['job_name'],
    },
  },
  {
    name: 'datastage_get_job_run_logs',
    description: 'Get logs for a specific job run. Requires both job_id and run_id.',
    inputSchema: {
      type: 'object',
      properties: {
        job_id: {
          type: 'string',
          description: 'The runtime job ID (from datastage_list_jobs)',
        },
        run_id: {
          type: 'string',
          description: 'The specific run ID (from datastage_get_job_runs)',
        },
      },
      required: ['job_id', 'run_id'],
    },
  },
  {
    name: 'datastage_list_flows',
    description: 'List all DataStage flows (design-time job definitions) in the configured project. Optionally filter by flow name pattern. Flows contain the complete job design including stages, links, and configurations.',
    inputSchema: {
      type: 'object',
      properties: {
        filter: {
          type: 'string',
          description: 'Optional filter pattern for flow names',
        },
      },
    },
  },
  {
    name: 'datastage_get_flow_details',
    description: 'Get detailed information about a specific DataStage flow including all stages, links, column definitions, and transformations. This provides the complete job design with all metadata.',
    inputSchema: {
      type: 'object',
      properties: {
        flow_id: {
          type: 'string',
          description: 'The flow ID (from datastage_list_flows)',
        },
      },
      required: ['flow_id'],
    },
  },
  {
    name: 'datastage_export_flow',
    description: 'Export DataStage flows with dependencies as a zip file using the /data_intg/v3/migration/zip_exports endpoint. The zip file contains the flow definition and all its dependencies (connections, environments, etc.). The flow_id can be obtained from datastage_list_flows.',
    inputSchema: {
      type: 'object',
      properties: {
        flow_id: {
          type: 'string',
          description: 'The flow ID to export (from datastage_list_flows)',
        },
        output_file: {
          type: 'string',
          description: 'Optional output filename (default: flow_<flow_id>.zip)',
        },
      },
      required: ['flow_id'],
    },
  },
  {
    name: 'datastage_import_flow',
    description: 'Import DataStage flows from a zip file using the /data_intg/v3/migration/zip_imports endpoint. This is an asynchronous operation that creates flows and their dependencies from an exported zip file. The API returns immediately with import status - use the returned import_id to check progress.',
    inputSchema: {
      type: 'object',
      properties: {
        zip_file_path: {
          type: 'string',
          description: 'Path to the zip file to import (can be absolute or relative to current directory)',
        },
        conflict_resolution: {
          type: 'string',
          enum: ['skip', 'rename', 'replace', 'rename_replace'],
          description: 'How to handle name conflicts: skip (default), rename (add suffix), replace (overwrite), rename_replace (use _DATASTAGE_ISX_IMPORT suffix)',
          default: 'skip',
        },
        on_failure: {
          type: 'string',
          enum: ['continue', 'stop'],
          description: 'Action on first failure: continue (default) or stop',
          default: 'continue',
        },
        include_dependencies: {
          type: 'boolean',
          description: 'Include dependencies (connections, parameter sets, etc.). Default: true',
          default: true,
        },
        enable_notification: {
          type: 'boolean',
          description: 'Enable notifications. Default: true',
          default: true,
        },
        import_only: {
          type: 'boolean',
          description: 'Skip flow compilation. Default: false',
          default: false,
        },
        replace_mode: {
          type: 'string',
          enum: ['soft', 'hard', 'force'],
          description: 'Replace mode when conflict_resolution is replace: soft (merge params), hard (replace all), force (replace even with type diff)',
        },
      },
      required: ['zip_file_path'],
    },
  },
  {
    name: 'datastage_run_job',
    description: 'Run a DataStage job. Optionally provide job parameters, environment variables, and parameter sets. Returns the run ID and status.',
    inputSchema: {
      type: 'object',
      properties: {
        job_id: {
          type: 'string',
          description: 'The job ID to run (from datastage_list_jobs)',
        },
        name: {
          type: 'string',
          description: 'Optional name for this job run',
        },
        description: {
          type: 'string',
          description: 'Optional description for this job run',
        },
        env_variables: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional environment variables in format ["key1=value1", "key2=value2"]',
        },
        job_parameters: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              value: { }
            },
            required: ['name', 'value']
          },
          description: 'Optional job parameters',
        },
      },
      required: ['job_id'],
    },
  },
  {
    name: 'datastage_compile_flow',
    description: 'Compile a DataStage flow to generate runtime assets. This must be done after modifying a flow before it can be run.',
    inputSchema: {
      type: 'object',
      properties: {
        flow_id: {
          type: 'string',
          description: 'The DataStage flow ID to compile',
        },
        runtime_type: {
          type: 'string',
          description: 'The type of runtime to use (e.g., dspxosh or Spark). Default is dspxosh',
        },
        enable_async_compile: {
          type: 'boolean',
          description: 'Whether to compile asynchronously. Default is false',
        },
      },
      required: ['flow_id'],
    },
  },
];

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'datastage_list_jobs':
        return await handleListJobs(args);
      
      case 'datastage_get_job_runs':
        return await handleGetJobRuns(args);
      
      case 'datastage_get_job_run_logs':
        return await handleGetJobRunLogs(args);
      
      case 'datastage_list_flows':
        return await handleListFlows(args);
      
      case 'datastage_get_flow_details':
        return await handleGetFlowDetails(args);
      
      case 'datastage_export_flow':
        return await handleExportFlow(args);
      
      case 'datastage_import_flow':
        return await handleImportFlow(args);
      
      case 'datastage_run_job':
        return await handleRunJob(args);
      
      case 'datastage_compile_flow':
        return await handleCompileFlow(args);
      
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    logger.error(`Tool execution failed: ${name}`, { error });
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// Tool handler
async function handleListJobs(_args: any) {
  logger.info('Listing DataStage jobs');
  const jobs = await cpdClient.listJobs();
  
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(jobs, null, 2),
      },
    ],
  };
}

async function handleGetJobRuns(args: any) {
  const { job_name, limit = 50 } = args;
  
  logger.info('Getting job runs', { job_name, limit });
  
  // First, find the job by name to get its ID from raw API response
  const jobsResponse = await cpdClient.listJobs();
  const results = jobsResponse?.results || [];
  
  // Find job by name in the results
  const job = results.find((j: any) => {
    const name = j.entity?.name || j.metadata?.name;
    return name && name.toLowerCase().includes(job_name.toLowerCase());
  });
  
  if (!job) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'Job not found', job_name }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  const jobId = job.metadata?.asset_id || job.metadata?.id;
  logger.info('Found job', { id: jobId, name: job.entity?.name || job.metadata?.name });
  
  try {
    const runsData = await cpdClient.getJobRuns(jobId, limit);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(runsData, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            job_id: jobId,
            job_name
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

async function handleGetJobRunLogs(args: any) {
  const { job_id, run_id } = args;
  
  if (!job_id || !run_id) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'Both job_id and run_id are required' }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  logger.info('Getting job run logs', { job_id, run_id });
  
  try {
    const logsData = await cpdClient.getJobRunLogs(job_id, run_id);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(logsData, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            job_id,
            run_id
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

async function handleListFlows(_args: any) {
  logger.info('Listing DataStage flows');
  const flows = await cpdClient.listDataStageFlows();
  
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(flows, null, 2),
      },
    ],
  };
}

async function handleGetFlowDetails(args: any) {
  const { flow_id } = args;
  
  if (!flow_id) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'flow_id is required' }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  logger.info('Getting flow details', { flow_id });
  
  try {
    const flowData = await cpdClient.getFlowDetails(flow_id);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(flowData, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            flow_id
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

async function handleExportFlow(args: any) {
  const { flow_id, output_file } = args;
  
  if (!flow_id) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'flow_id is required' }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  logger.info('Exporting flow with dependencies', { flow_id, output_file });
  
  try {
    const zipBuffer = await cpdClient.exportAsset(flow_id);
    const filename = output_file || `flow_${flow_id}.zip`;
    
    // Get current working directory (where Bob is running)
    const cwd = process.cwd();
    const outputPath = path.join(cwd, filename);
    
    // Write the zip file to disk
    fs.writeFileSync(outputPath, zipBuffer);
    
    logger.info('Flow exported successfully with dependencies', { outputPath, size: zipBuffer.length });
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            flow_id,
            filename,
            output_path: outputPath,
            size_bytes: zipBuffer.length,
            message: `Flow with dependencies exported successfully to: ${outputPath}`
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            flow_id
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

async function handleImportFlow(args: any) {
  const {
    zip_file_path,
    conflict_resolution = 'skip',
    on_failure = 'continue',
    include_dependencies = true,
    enable_notification = true,
    import_only = false,
    replace_mode
  } = args;
  
  if (!zip_file_path) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'zip_file_path is required' }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  logger.info('Importing flows from zip file', { zip_file_path, conflict_resolution, on_failure });
  
  try {
    // Resolve the file path (handle relative paths)
    const resolvedPath = path.isAbsolute(zip_file_path)
      ? zip_file_path
      : path.join(process.cwd(), zip_file_path);
    
    // Check if file exists
    if (!fs.existsSync(resolvedPath)) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              error: 'Zip file not found',
              zip_file_path,
              resolved_path: resolvedPath
            }, null, 2),
          },
        ],
        isError: true,
      };
    }
    
    const importResult = await cpdClient.importFlows(resolvedPath, {
      conflict_resolution,
      on_failure,
      include_dependencies,
      enable_notification,
      import_only,
      replace_mode
    });
    
    logger.info('Flow import request submitted', {
      importId: importResult?.metadata?.id,
      status: importResult?.entity?.import_data_flows?.[0]?.status
    });
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            message: 'Import request submitted successfully. This is an asynchronous operation.',
            import_id: importResult?.metadata?.id,
            import_status: importResult?.entity?.import_data_flows?.[0]?.status,
            import_name: importResult?.metadata?.name,
            details: importResult
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            zip_file_path
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

async function handleRunJob(args: any) {
  const { job_id, name, description, env_variables, job_parameters } = args;
  
  if (!job_id) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'job_id is required' }, null, 2),
        },
      ],
      isError: true,
    };
  }
  
  logger.info('Running DataStage job', { job_id, name });
  
  try {
    const result = await cpdClient.runJob(job_id, {
      name,
      description,
      env_variables,
      job_parameters,
    });
    
    logger.info('Job run submitted successfully', {
      jobId: job_id,
      runId: result?.metadata?.asset_id
    });
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            message: 'Job run submitted successfully',
            job_id,
            run_id: result?.metadata?.asset_id,
            status: result?.entity?.job_run?.state,
            details: result
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            job_id
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

/**
 * Handle datastage_compile_flow tool
 */
async function handleCompileFlow(args: any) {
  const { flow_id, runtime_type, enable_async_compile } = args;
  
  if (!flow_id) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: 'flow_id is required' }, null, 2),
        },
      ],
      isError: true,
    };
  }

  try {
    logger.info('Compiling flow', { flow_id, runtime_type, enable_async_compile });
    
    const options: any = {};
    if (runtime_type) options.runtime_type = runtime_type;
    if (enable_async_compile !== undefined) options.enable_async_compile = enable_async_compile;
    
    const result = await cpdClient.compileFlow(flow_id, options);
    
    logger.info('Flow compile result', { result });
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            message: 'Flow compilation submitted successfully',
            flow_id,
            result: result?.message?.result,
            runtime_type: result?.message?.runtime_type,
            details: result
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            flow_id
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
}

// Start server
async function main() {
  logger.info('Starting DataStage MCP Server (Simplified)');
  
  // Validate configuration
  if (!ENV.CPD_URL) {
    throw new Error('CPD_URL environment variable is required');
  }
  
  if (!ENV.CPD_USERNAME || !ENV.CPD_PASSWORD) {
    throw new Error('CPD_USERNAME and CPD_PASSWORD are required');
  }
  
  if (!ENV.CPD_PROJECT_ID) {
    throw new Error('CPD_PROJECT_ID is required');
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  logger.info('DataStage MCP Server running');
}

main().catch((error) => {
  logger.error('Server failed to start', { error });
  process.exit(1);
});

// Made with Bob
