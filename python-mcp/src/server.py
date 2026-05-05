#!/usr/bin/env python3
"""
DataStage MCP Server - Simplified Version
Provides Bob IDE with basic DataStage job listing capability using FastMCP
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from fastmcp import FastMCP
from .auth.auth_manager import AuthManager
from .api.cpd_client import CPDClient
from .utils.logger import logger
from .config.constants import ENV

# Initialize managers
auth_manager = AuthManager()
cpd_client = CPDClient(auth_manager)

# Create FastMCP server
mcp = FastMCP("datastage-server")


@mcp.tool()
async def datastage_list_projects(limit: int = 100, bss_account_id: Optional[str] = None) -> str:
    """
    List all DataStage projects accessible to the authenticated user.
    Returns project names and IDs that can be used with other tools.
    
    Args:
        limit: Maximum number of projects to return (default: 100)
        bss_account_id: Optional BSS Account ID to filter projects by IBM Cloud account
    
    Returns:
        JSON string with projects list including project IDs and names
    """
    logger.info('Listing DataStage projects', {'limit': limit, 'bss_account_id': bss_account_id})
    
    try:
        projects_data = await cpd_client.list_projects(limit, bss_account_id)
        
        # Extract simplified project info for easier reading
        projects_list = []
        for project in projects_data.get('resources', []):
            metadata = project.get('metadata', {})
            entity = project.get('entity', {})
            
            project_info = {
                'project_id': metadata.get('guid'),
                'name': entity.get('name'),
                'description': entity.get('description'),
                'created_at': metadata.get('created_at'),
                'bss_account_id': metadata.get('bss_account_id')
            }
            projects_list.append(project_info)
        
        result = {
            'total_results': projects_data.get('total_results', 0),
            'projects': projects_list,
            'message': 'Use the project_id from this list in other DataStage tools'
        }
        
        return json.dumps(result, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'message': 'Failed to list projects'
        }, indent=2)


@mcp.tool()
async def datastage_select_project(project_id: str) -> str:
    """
    Select a project to use for subsequent DataStage operations.
    This sets the default project ID so you don't need to specify it in every tool call.
    
    Args:
        project_id: The project ID to use (from datastage_list_projects)
    
    Returns:
        JSON string with confirmation
    """
    logger.info('Selecting project', {'project_id': project_id})
    
    try:
        cpd_client.set_project_id(project_id)
        return json.dumps({
            'success': True,
            'message': f'Project {project_id} selected successfully',
            'project_id': project_id,
            'note': 'This project will be used for all subsequent operations unless overridden'
        }, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'project_id': project_id
        }, indent=2)


@mcp.tool()
async def datastage_list_jobs(filter: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """
    List all DataStage jobs in a project. Optionally filter by job name pattern.
    
    Args:
        filter: Optional filter pattern for job names
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with job list
    """
    logger.info('Listing DataStage jobs', {'project_id': project_id})
    jobs = await cpd_client.list_jobs(project_id, filter)
    return json.dumps(jobs, indent=2)


@mcp.tool()
async def datastage_get_job_runs(job_name: str, limit: int = 50, project_id: Optional[str] = None) -> str:
    """
    Get run history for a specific DataStage job using the /v2/jobs API.
    
    Args:
        job_name: Name of the DataStage job
        limit: Maximum number of runs to return (default: 50)
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with job runs
    """
    logger.info('Getting job runs', {'job_name': job_name, 'limit': limit, 'project_id': project_id})
    
    # First, find the job by name to get its ID from raw API response
    jobs_response = await cpd_client.list_jobs(project_id)
    results = jobs_response.get('results', [])
    
    # Find job by name in the results
    job = None
    for j in results:
        name = j.get('entity', {}).get('name') or j.get('metadata', {}).get('name')
        if name and job_name.lower() in name.lower():
            job = j
            break
    
    if not job:
        return json.dumps({'error': 'Job not found', 'job_name': job_name}, indent=2)
    
    job_id = job.get('metadata', {}).get('asset_id') or job.get('metadata', {}).get('id')
    logger.info('Found job', {'id': job_id, 'name': job.get('entity', {}).get('name')})
    
    try:
        runs_data = await cpd_client.get_job_runs(job_id, limit, project_id)
        return json.dumps(runs_data, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'job_id': job_id,
            'job_name': job_name
        }, indent=2)


@mcp.tool()
async def datastage_get_job_run_logs(job_id: str, run_id: str, project_id: Optional[str] = None) -> str:
    """
    Get logs for a specific job run. Requires both job_id and run_id.
    
    Args:
        job_id: The runtime job ID (from datastage_list_jobs)
        run_id: The specific run ID (from datastage_get_job_runs)
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with job run logs
    """
    if not job_id or not run_id:
        return json.dumps({'error': 'Both job_id and run_id are required'}, indent=2)
    
    logger.info('Getting job run logs', {'job_id': job_id, 'run_id': run_id, 'project_id': project_id})
    
    try:
        logs_data = await cpd_client.get_job_run_logs(job_id, run_id, project_id)
        return json.dumps(logs_data, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'job_id': job_id,
            'run_id': run_id
        }, indent=2)


@mcp.tool()
async def datastage_list_flows(filter: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """
    List all DataStage flows (design-time job definitions) in a project.
    Optionally filter by flow name pattern. Flows contain the complete job design
    including stages, links, and configurations.
    
    Args:
        filter: Optional filter pattern for flow names
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with flow list
    """
    logger.info('Listing DataStage flows', {'project_id': project_id})
    flows = await cpd_client.list_datastage_flows(filter, project_id)
    return json.dumps(flows, indent=2)


@mcp.tool()
async def datastage_get_flow_details(flow_id: str, project_id: Optional[str] = None) -> str:
    """
    Get detailed information about a specific DataStage flow including all stages,
    links, column definitions, and transformations. This provides the complete job
    design with all metadata.
    
    Args:
        flow_id: The flow ID (from datastage_list_flows)
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with flow details
    """
    if not flow_id:
        return json.dumps({'error': 'flow_id is required'}, indent=2)
    
    logger.info('Getting flow details', {'flow_id': flow_id, 'project_id': project_id})
    
    try:
        flow_data = await cpd_client.get_flow_details(flow_id, project_id)
        return json.dumps(flow_data, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'flow_id': flow_id
        }, indent=2)


@mcp.tool()
async def datastage_export_flow(flow_id: str, output_file: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """
    Export DataStage flows with dependencies as a zip file using the
    /data_intg/v3/migration/zip_exports endpoint. The zip file contains the flow
    definition and all its dependencies (connections, environments, etc.).
    The flow_id can be obtained from datastage_list_flows.
    
    Args:
        flow_id: The flow ID to export (from datastage_list_flows)
        output_file: Optional output filename (default: flow_<flow_id>.zip)
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with export result
    """
    if not flow_id:
        return json.dumps({'error': 'flow_id is required'}, indent=2)
    
    logger.info('Exporting flow with dependencies', {'flow_id': flow_id, 'output_file': output_file, 'project_id': project_id})
    
    try:
        zip_buffer = await cpd_client.export_asset(flow_id, project_id)
        filename = output_file or f'flow_{flow_id}.zip'
        
        # Get workspace directory from environment variable (set by wrapper script)
        # Falls back to current directory if not set
        workspace_dir = os.getenv('WORKSPACE_DIR')
        if workspace_dir:
            cwd = Path(workspace_dir)
        else:
            cwd = Path.cwd()
        
        output_path = cwd / filename
        
        # Write the zip file to disk
        output_path.write_bytes(zip_buffer)
        
        logger.info('Flow exported successfully with dependencies', {
            'output_path': str(output_path),
            'size': len(zip_buffer)
        })
        
        return json.dumps({
            'success': True,
            'flow_id': flow_id,
            'filename': filename,
            'output_path': str(output_path),
            'size_bytes': len(zip_buffer),
            'message': f'Flow with dependencies exported successfully to: {output_path}'
        }, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'flow_id': flow_id
        }, indent=2)


@mcp.tool()
async def datastage_import_flow(
    zip_file_path: str,
    conflict_resolution: str = 'skip',
    on_failure: str = 'continue',
    include_dependencies: bool = True,
    enable_notification: bool = True,
    import_only: bool = False,
    replace_mode: Optional[str] = None,
    project_id: Optional[str] = None
) -> str:
    """
    Import DataStage flows from a zip file using the /data_intg/v3/migration/zip_imports
    endpoint. This is an asynchronous operation that creates flows and their dependencies
    from an exported zip file. The API returns immediately with import status - use the
    returned import_id to check progress.
    
    Args:
        zip_file_path: Path to the zip file to import (can be absolute or relative to current directory)
        conflict_resolution: How to handle name conflicts: skip (default), rename (add suffix), replace (overwrite), rename_replace (use _DATASTAGE_ISX_IMPORT suffix)
        on_failure: Action on first failure: continue (default) or stop
        include_dependencies: Include dependencies (connections, parameter sets, etc.). Default: true
        enable_notification: Enable notifications. Default: true
        import_only: Skip flow compilation. Default: false
        replace_mode: Replace mode when conflict_resolution is replace: soft (merge params), hard (replace all), force (replace even with type diff)
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with import result
    """
    if not zip_file_path:
        return json.dumps({'error': 'zip_file_path is required'}, indent=2)
    
    logger.info('Importing flows from zip file', {
        'zip_file_path': zip_file_path,
        'conflict_resolution': conflict_resolution,
        'on_failure': on_failure,
        'project_id': project_id
    })
    
    try:
        # Get workspace directory from environment variable
        workspace_dir = os.getenv('WORKSPACE_DIR')
        if workspace_dir:
            base_dir = Path(workspace_dir)
        else:
            base_dir = Path.cwd()
        
        # Resolve the file path (handle relative paths)
        file_path = Path(zip_file_path)
        if not file_path.is_absolute():
            file_path = base_dir / zip_file_path
        
        # Check if file exists
        if not file_path.exists():
            return json.dumps({
                'error': 'Zip file not found',
                'zip_file_path': zip_file_path,
                'resolved_path': str(file_path)
            }, indent=2)
        
        import_result = await cpd_client.import_flows(
            str(file_path),
            conflict_resolution=conflict_resolution,
            on_failure=on_failure,
            include_dependencies=include_dependencies,
            enable_notification=enable_notification,
            import_only=import_only,
            replace_mode=replace_mode,
            project_id=project_id
        )
        
        # Safely extract import status
        import_data_flows = import_result.get('entity', {}).get('import_data_flows', [])
        import_status = import_data_flows[0].get('status') if import_data_flows else 'unknown'
        
        logger.info('Flow import request submitted', {
            'import_id': import_result.get('metadata', {}).get('id'),
            'status': import_status
        })
        
        return json.dumps({
            'success': True,
            'message': 'Import request submitted successfully. This is an asynchronous operation.',
            'import_id': import_result.get('metadata', {}).get('id'),
            'import_status': import_status,
            'import_name': import_result.get('metadata', {}).get('name'),
            'details': import_result
        }, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'zip_file_path': zip_file_path
        }, indent=2)


@mcp.tool()
async def datastage_run_job(
    job_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    env_variables: Optional[list] = None,
    job_parameters: Optional[list] = None,
    project_id: Optional[str] = None
) -> str:
    """
    Run a DataStage job. Optionally provide job parameters, environment variables,
    and parameter sets. Returns the run ID and status.
    
    Args:
        job_id: The job ID to run (from datastage_list_jobs)
        name: Optional name for this job run
        description: Optional description for this job run
        env_variables: Optional environment variables in format ["key1=value1", "key2=value2"]
        job_parameters: Optional job parameters as list of dicts with 'name' and 'value' keys
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with run result
    """
    if not job_id:
        return json.dumps({'error': 'job_id is required'}, indent=2)
    
    logger.info('Running DataStage job', {'job_id': job_id, 'name': name, 'project_id': project_id})
    
    try:
        result = await cpd_client.run_job(
            job_id,
            name=name,
            description=description,
            env_variables=env_variables,
            job_parameters=job_parameters,
            project_id=project_id
        )
        
        logger.info('Job run submitted successfully', {
            'job_id': job_id,
            'run_id': result.get('metadata', {}).get('asset_id')
        })
        
        return json.dumps({
            'success': True,
            'message': 'Job run submitted successfully',
            'job_id': job_id,
            'run_id': result.get('metadata', {}).get('asset_id'),
            'status': result.get('entity', {}).get('job_run', {}).get('state'),
            'details': result
        }, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'job_id': job_id
        }, indent=2)


@mcp.tool()
async def datastage_compile_flow(
    flow_id: str,
    runtime_type: Optional[str] = None,
    enable_async_compile: Optional[bool] = None,
    project_id: Optional[str] = None
) -> str:
    """
    Compile a DataStage flow to generate runtime assets. This must be done after
    modifying a flow before it can be run.
    
    Args:
        flow_id: The DataStage flow ID to compile
        runtime_type: The type of runtime to use (e.g., dspxosh or Spark). Default is dspxosh
        enable_async_compile: Whether to compile asynchronously. Default is false
        project_id: Optional project ID (uses selected project if not provided)
    
    Returns:
        JSON string with compile result
    """
    if not flow_id:
        return json.dumps({'error': 'flow_id is required'}, indent=2)
    
    try:
        logger.info('Compiling flow', {
            'flow_id': flow_id,
            'runtime_type': runtime_type,
            'enable_async_compile': enable_async_compile,
            'project_id': project_id
        })
        
        result = await cpd_client.compile_flow(
            flow_id,
            runtime_type=runtime_type,
            enable_async_compile=enable_async_compile,
            project_id=project_id
        )
        
        logger.info('Flow compile result', {'result': result})
        
        return json.dumps({
            'success': True,
            'message': 'Flow compilation submitted successfully',
            'flow_id': flow_id,
            'result': result.get('message', {}).get('result'),
            'runtime_type': result.get('message', {}).get('runtime_type'),
            'details': result
        }, indent=2)
    except Exception as error:
        return json.dumps({
            'error': str(error),
            'flow_id': flow_id
        }, indent=2)


@mcp.tool()
async def datastage_convert_flow_to_python(
    zip_file_path: str,
    output_path: str = "generated_code",
    mode: str = "file_per_flow",
    persist_topology: bool = False
) -> str:
    """
    Convert exported DataStage flow (zip file) to Python SDK code using IBM's
    DataStage Python SDK code generator. This allows you to programmatically
    recreate and modify DataStage flows using Python.
    
    Args:
        zip_file_path: Path to the exported flow zip file (can be absolute or relative to current directory)
        output_path: Directory where generated Python code will be saved (can be absolute or relative, default: generated_code)
        mode: Code generation mode - "file_per_flow" or "single_file" (default: file_per_flow)
        persist_topology: Whether to persist topology information (default: false)
    
    Returns:
        JSON string with conversion result
    """
    if not zip_file_path:
        return json.dumps({'error': 'zip_file_path is required'}, indent=2)
    
    logger.info('Converting DataStage flow to Python SDK code', {
        'zip_file_path': zip_file_path,
        'output_path': output_path,
        'mode': mode
    })
    
    try:
        # Import IBM DataStage SDK modules
        from ibm_watsonx_data_integration.common.auth import ICP4DAuthenticator
        from ibm_watsonx_data_integration.platform import Platform
        from ibm_watsonx_data_integration.services.datastage.codegen import PythonGenerator
        
        # Get workspace directory from environment variable
        workspace_dir = os.getenv('WORKSPACE_DIR')
        if workspace_dir:
            base_dir = Path(workspace_dir)
        else:
            base_dir = Path.cwd()
        
        # Resolve file paths (handle relative paths)
        zip_path = Path(zip_file_path)
        if not zip_path.is_absolute():
            zip_path = base_dir / zip_file_path
        
        if not zip_path.exists():
            return json.dumps({
                'error': 'Zip file not found',
                'zip_file_path': zip_file_path,
                'resolved_path': str(zip_path),
                'workspace_directory': str(base_dir)
            }, indent=2)
        
        output_dir = Path(output_path)
        if not output_dir.is_absolute():
            output_dir = base_dir / output_path
        
        # Create authenticator using environment variables
        auth = ICP4DAuthenticator(
            url=ENV.CPD_URL,
            username=ENV.CPD_USERNAME,
            password=ENV.CPD_PASSWORD
        )
        
        # Initialize platform (required for SDK)
        platform = Platform(auth, base_url=ENV.CPD_URL)
        
        # Configure code generator
        code_gen = PythonGenerator()
        code_gen.configuration.mode = mode
        code_gen.configuration.authenticator = auth
        code_gen.configuration.project_id = ENV.CPD_PROJECT_ID
        code_gen.configuration.persist_topology = persist_topology
        
        # Generate Python code from flow
        logger.info('Generating Python code from DataStage flow', {
            'input': str(zip_path),
            'output': str(output_dir)
        })
        
        code_gen.generate(input_path=str(zip_path), output_path=str(output_dir))
        
        logger.info('Successfully generated Python SDK code', {
            'output_path': str(output_dir)
        })
        
        # Post-process generated files to replace IAM auth with ICP4D auth
        files_modified = []
        for py_file in output_dir.glob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check if file contains IAM authentication code
                if 'IAMAuthenticator' in content and 'api_key' in content:
                    logger.info(f'Replacing IAM auth with ICP4D auth in {py_file.name}')
                    
                    # Replace the IAM authentication block with ICP4D authentication
                    # Pattern to match the autogenerated IAM auth code
                    iam_pattern = r'# This code was autogenerated by PythonGenerator\s*\nfrom ibm_watsonx_data_integration import \*\s*\nfrom ibm_watsonx_data_integration\.common\.auth import IAMAuthenticator\s*\nfrom ibm_watsonx_data_integration\.services\.datastage import \*\s*\n\s*\napi_key = "[^"]*"\s*\nauth = IAMAuthenticator\(api_key=api_key, base_auth_url="[^"]*"\)\s*\nplatform = Platform\(auth, base_url="[^"]*", base_api_url="[^"]*"\)\s*\nproject = platform\.projects\.get\(project_id="[^"]*"\)'
                    
                    # Replacement ICP4D authentication code
                    icp4d_replacement = f'''from ibm_watsonx_data_integration.common.auth import ICP4DAuthenticator
from ibm_watsonx_data_integration.common.auth import IAMAuthenticator
from ibm_watsonx_data_integration import Platform
from ibm_watsonx_data_integration.services.datastage import *

# Replace with your actual username and password
auth = ICP4DAuthenticator(                   # pragma: allowlist secret
    url='{ENV.CPD_URL}',                  # pragma: allowlist secret
    username='{ENV.CPD_USERNAME}',                # pragma: allowlist secret
    password='{ENV.CPD_PASSWORD}'                 # pragma: allowlist secret
    # zen_api_key='your-zen-api-key'         # pragma: allowlist secret
)

from ibm_watsonx_data_integration.platform import Platform
platform = Platform(auth, base_url='{ENV.CPD_URL}')
project = platform.projects.get(project_id="{ENV.CPD_PROJECT_ID}")'''
                    
                    # Try regex replacement first
                    import re
                    new_content = re.sub(iam_pattern, icp4d_replacement, content, flags=re.MULTILINE)
                    
                    # If regex didn't match, try simpler string replacement
                    if new_content == content:
                        # Find and replace the imports section
                        if '# This code was autogenerated by PythonGenerator' in content:
                            lines = content.split('\n')
                            new_lines = []
                            skip_until_project = False
                            
                            for i, line in enumerate(lines):
                                if '# This code was autogenerated by PythonGenerator' in line:
                                    # Add the new authentication code
                                    new_lines.append(icp4d_replacement)
                                    skip_until_project = True
                                elif skip_until_project:
                                    # Skip lines until we find the project line
                                    if line.strip().startswith('project = platform.projects.get'):
                                        skip_until_project = False
                                        # Skip the old project line since we already added it in replacement
                                        continue
                                else:
                                    new_lines.append(line)
                            
                            new_content = '\n'.join(new_lines)
                    
                    # Write the modified content back
                    if new_content != content:
                        py_file.write_text(new_content, encoding='utf-8')
                        files_modified.append(py_file.name)
                        logger.info(f'Successfully modified {py_file.name}')
                    
            except Exception as e:
                logger.error(f'Failed to modify {py_file.name}: {str(e)}')
        
        result_message = 'DataStage flow successfully converted to Python SDK code'
        if files_modified:
            result_message += f'. Modified {len(files_modified)} file(s) to use ICP4D authentication'
        
        return json.dumps({
            'success': True,
            'message': result_message,
            'input_file': str(zip_path),
            'output_directory': str(output_dir),
            'mode': mode,
            'project_id': ENV.CPD_PROJECT_ID,
            'files_generated': 'Check output directory for generated Python files',
            'files_modified': files_modified if files_modified else 'No files needed modification'
        }, indent=2)
        
    except ImportError as error:
        return json.dumps({
            'error': 'IBM DataStage SDK not installed',
            'message': str(error),
            'solution': 'Install with: pip install ibm-watsonx-data-integration'
        }, indent=2)
    except Exception as error:
        logger.error('Flow conversion failed', {'error': str(error)})
        return json.dumps({
            'error': str(error),
            'zip_file_path': zip_file_path,
            'output_path': output_path
        }, indent=2)


def main():
    """Main entry point for the server"""
    logger.info('Starting DataStage MCP Server with Dynamic Project Selection')
    
    # Validate configuration
    if not ENV.CPD_URL:
        raise Exception('CPD_URL environment variable is required')
    
    if not ENV.CPD_USERNAME or not ENV.CPD_PASSWORD:
        raise Exception('CPD_USERNAME and CPD_PASSWORD are required')
    
    # CPD_PROJECT_ID is now optional - can be selected dynamically
    if ENV.CPD_PROJECT_ID:
        logger.info('Using default project from environment', {'project_id': ENV.CPD_PROJECT_ID})
    else:
        logger.info('No default project set - use datastage_list_projects and datastage_select_project to choose a project')
    
    logger.info('DataStage MCP Server running')
    
    # Run the FastMCP server
    mcp.run()


if __name__ == '__main__':
    main()


# Made with Bob