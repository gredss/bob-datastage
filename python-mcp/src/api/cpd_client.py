"""
Cloud Pak for Data API Client - Simplified Version
Only includes working functionality: listing DataStage jobs
"""

import httpx
from pathlib import Path
from typing import Any, Dict, Optional
from ..auth.auth_manager import AuthManager
from ..config.constants import ENV, API_ENDPOINTS, TIMEOUT_CONFIG, RETRY_CONFIG
from ..utils.logger import logger
from ..utils.retry import retry_with_backoff


class APIError(Exception):
    """API error"""
    def __init__(self, message: str, status_code: int, details: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class CPDClient:
    """Cloud Pak for Data API Client"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.base_url = ENV.CPD_URL
        self._selected_project_id: Optional[str] = None
    
    def set_project_id(self, project_id: str):
        """Set the project ID to use for subsequent operations"""
        self._selected_project_id = project_id
        logger.info('Project ID set', {'project_id': project_id})
    
    async def _get_project_id(self, project_id: Optional[str] = None) -> str:
        """
        Get project ID with priority:
        1. Explicitly provided project_id parameter
        2. Previously selected project_id via set_project_id()
        3. Environment variable CPD_PROJECT_ID
        """
        # Priority 1: Explicit parameter
        if project_id:
            logger.info('Using explicit project ID parameter', {'project_id': project_id})
            return project_id
        
        # Priority 2: Selected project ID
        if self._selected_project_id:
            logger.info('Using selected project ID', {'project_id': self._selected_project_id})
            return self._selected_project_id
        
        # Priority 3: Environment variable
        if ENV.CPD_PROJECT_ID:
            logger.info('Using project ID from environment', {'project_id': ENV.CPD_PROJECT_ID})
            return ENV.CPD_PROJECT_ID
        
        raise Exception('No project ID available. Use datastage_list_projects to select a project or set CPD_PROJECT_ID environment variable')
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an authenticated HTTP request"""
        token = await self.auth_manager.get_token()
        
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        
        # Ensure base_url doesn't end with / and endpoint starts with /
        base = self.base_url.rstrip('/')
        path = endpoint if endpoint.startswith('/') else f'/{endpoint}'
        url = f'{base}{path}'
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                timeout=kwargs.pop('timeout', TIMEOUT_CONFIG.API_REQUEST),
                **kwargs
            )
            response.raise_for_status()
            return response
    
    async def list_projects(self, limit: int = 100, bss_account_id: Optional[str] = None) -> Any:
        """
        List all projects accessible to the authenticated user.
        
        Args:
            limit: Maximum number of projects to return (default: 100)
            bss_account_id: Optional BSS Account ID to filter projects
        
        Returns:
            Dictionary containing projects list with metadata including project IDs
        """
        logger.info('Listing projects', {'limit': limit, 'bss_account_id': bss_account_id})
        
        try:
            endpoint = API_ENDPOINTS.PROJECTS(limit, bss_account_id)
            logger.info('Making request to:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Projects response received', {
                'status': response.status_code,
                'total_results': data.get('total_results', 0)
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('/v2/projects request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to list projects: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def list_jobs(self, project_id: Optional[str] = None, filter: Optional[str] = None) -> Any:
        """List all runtime jobs in the project (from /v2/jobs API)"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Listing runtime jobs from /v2/jobs', {'project_id': project_id, 'filter': filter})
        
        try:
            endpoint = API_ENDPOINTS.JOBS(project_id)
            logger.info('Making request to:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Response received', {
                'status': response.status_code,
                'data_keys': list(data.keys()) if isinstance(data, dict) else None
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('/v2/jobs request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to list jobs: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def get_job_runs(self, job_id: str, limit: int = 50, project_id: Optional[str] = None) -> Any:
        """Get job runs for a specific job"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Fetching job runs', {'job_id': job_id, 'project_id': project_id, 'limit': limit})
        
        try:
            endpoint = API_ENDPOINTS.JOB_RUNS(job_id, project_id)
            logger.info('Requesting job runs from:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Job runs response received', {
                'status': response.status_code,
                'data_keys': list(data.keys()) if isinstance(data, dict) else None
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Job runs request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to fetch job runs: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def get_job_run_logs(self, job_id: str, run_id: str, project_id: Optional[str] = None) -> Any:
        """Get logs for a specific job run"""
        try:
            project_id = await self._get_project_id(project_id)
            endpoint = API_ENDPOINTS.JOB_RUN_LOGS(job_id, run_id, project_id)
            
            logger.info('Fetching job run logs', {'job_id': job_id, 'run_id': run_id, 'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Job run logs retrieved successfully', {
                'job_id': job_id,
                'run_id': run_id,
                'has_logs': bool(data)
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Failed to fetch job run logs', {
                'job_id': job_id,
                'run_id': run_id,
                'status': status,
                'message': message
            })
            
            raise APIError(
                f'Failed to fetch job run logs: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def run_job(
        self,
        job_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        env_variables: Optional[list] = None,
        job_parameters: Optional[list] = None,
        parameter_sets: Optional[list] = None,
        project_id: Optional[str] = None
    ) -> Any:
        """Run a DataStage job"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Running DataStage job', {'job_id': job_id, 'project_id': project_id})
        
        try:
            endpoint = API_ENDPOINTS.RUN_JOB(job_id, project_id)
            
            # Build request body
            request_body: Dict[str, Any] = {'job_run': {}}
            
            if name:
                request_body['job_run']['name'] = name
            if description:
                request_body['job_run']['description'] = description
            
            if env_variables or job_parameters or parameter_sets:
                request_body['job_run']['configuration'] = {}
                
                if env_variables:
                    request_body['job_run']['configuration']['env_variables'] = env_variables
            
            if job_parameters:
                request_body['job_run']['job_parameters'] = job_parameters
            
            if parameter_sets:
                request_body['job_run']['parameter_sets'] = parameter_sets
            
            logger.info('Submitting job run request', {'endpoint': endpoint, 'request_body': request_body})
            
            async def make_request():
                return await self._make_request('POST', endpoint, json=request_body)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Job run submitted successfully', {
                'status': response.status_code,
                'run_id': data.get('metadata', {}).get('asset_id')
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Job run request failed', {
                'job_id': job_id,
                'status': status,
                'message': message
            })
            
            raise APIError(
                f'Failed to run job: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def compile_flow(
        self,
        flow_id: str,
        runtime_type: Optional[str] = None,
        enable_sql_pushdown: Optional[bool] = None,
        enable_async_compile: Optional[bool] = None,
        enable_pushdown_source: Optional[bool] = None,
        enable_push_processing_to_source: Optional[bool] = None,
        enable_push_join_to_source: Optional[bool] = None,
        enable_pushdown_target: Optional[bool] = None,
        project_id: Optional[str] = None
    ) -> Any:
        """Compile a DataStage flow"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Compiling DataStage flow', {'flow_id': flow_id, 'project_id': project_id})
        
        try:
            # Build query parameters
            params = {'project_id': project_id}
            
            if runtime_type:
                params['runtime_type'] = runtime_type
            if enable_sql_pushdown is not None:
                params['enable_sql_pushdown'] = str(enable_sql_pushdown).lower()
            if enable_async_compile is not None:
                params['enable_async_compile'] = str(enable_async_compile).lower()
            if enable_pushdown_source is not None:
                params['enable_pushdown_source'] = str(enable_pushdown_source).lower()
            if enable_push_processing_to_source is not None:
                params['enable_push_processing_to_source'] = str(enable_push_processing_to_source).lower()
            if enable_push_join_to_source is not None:
                params['enable_push_join_to_source'] = str(enable_push_join_to_source).lower()
            if enable_pushdown_target is not None:
                params['enable_pushdown_target'] = str(enable_pushdown_target).lower()
            
            # Build endpoint with query params
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            endpoint = f'/data_intg/v3/ds_codegen/compile/{flow_id}?{query_string}'
            
            logger.info('Submitting flow compile request', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('POST', endpoint, json={})
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Flow compile submitted successfully', {
                'status': response.status_code,
                'result': data.get('message', {}).get('result')
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Flow compile request failed', {
                'flow_id': flow_id,
                'status': status,
                'message': message
            })
            
            raise APIError(
                f'Failed to compile flow: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def list_datastage_flows(self, filter: Optional[str] = None, project_id: Optional[str] = None) -> Any:
        """List all DataStage flows (design-time artifacts) in the project"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Listing DataStage flows from /data_intg/v3/data_intg_flows', {
            'project_id': project_id,
            'filter': filter
        })
        
        try:
            endpoint = API_ENDPOINTS.FLOWS(project_id)
            logger.info('Making request to:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Flows response received', {
                'status': response.status_code,
                'data_keys': list(data.keys()) if isinstance(data, dict) else None,
                'total_count': data.get('total_count') if isinstance(data, dict) else None
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('/data_intg/v3/data_intg_flows request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to list DataStage flows: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def get_flow_details(self, flow_id: str, project_id: Optional[str] = None) -> Any:
        """Get detailed flow information including stages, links, and column definitions"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Fetching flow details', {'flow_id': flow_id, 'project_id': project_id})
        
        try:
            endpoint = API_ENDPOINTS.FLOW_DETAILS(flow_id, project_id)
            logger.info('Requesting flow details from:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request('GET', endpoint)
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            logger.info('Flow details response received', {
                'status': response.status_code,
                'has_entity': 'entity' in data if isinstance(data, dict) else False
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Flow details request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to fetch flow details: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def export_asset(self, flow_id: str, project_id: Optional[str] = None) -> bytes:
        """Export DataStage flows with dependencies as a zip file"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Exporting flow with dependencies', {'flow_id': flow_id, 'project_id': project_id})
        
        try:
            endpoint = f"{API_ENDPOINTS.EXPORT_FLOWS(project_id)}&id={flow_id}&type=data_intg_flow"
            logger.info('Requesting flow export from migration API:', {'endpoint': endpoint})
            
            async def make_request():
                return await self._make_request(
                    'POST',
                    endpoint,
                    json={},
                    headers={
                        'Accept': 'application/octet-stream',
                        'Content-Type': 'application/json'
                    }
                )
            
            response = await retry_with_backoff(make_request)
            
            logger.info('Flow export response received', {
                'status': response.status_code,
                'content_type': response.headers.get('content-type'),
                'content_length': response.headers.get('content-length')
            })
            
            return response.content
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Flow export request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to export flow with dependencies: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise
    
    async def import_flows(
        self,
        zip_file_path: str,
        conflict_resolution: str = 'skip',
        on_failure: str = 'continue',
        include_dependencies: bool = True,
        enable_notification: bool = True,
        import_only: bool = False,
        replace_mode: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Any:
        """Import DataStage flows from a zip file"""
        project_id = await self._get_project_id(project_id)
        
        logger.info('Importing flows from zip file', {
            'zip_file_path': zip_file_path,
            'project_id': project_id
        })
        
        try:
            # Read the zip file as binary data
            file_path = Path(zip_file_path)
            file_buffer = file_path.read_bytes()
            file_name = file_path.name
            
            # Build query parameters
            params = {
                'project_id': project_id,
                'file_name': file_name,
                'conflict_resolution': conflict_resolution,
                'on_failure': on_failure,
                'include_dependencies': str(include_dependencies).lower(),
                'enable_notification': str(enable_notification).lower(),
                'import_only': str(import_only).lower()
            }
            
            if replace_mode:
                params['replace_mode'] = replace_mode
            
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            endpoint = f'/data_intg/v3/migration/zip_imports?{query_string}'
            
            logger.info('Requesting flow import from migration API:', {
                'endpoint': endpoint,
                'file_size': len(file_buffer)
            })
            
            async def make_request():
                return await self._make_request(
                    'POST',
                    endpoint,
                    content=file_buffer,
                    headers={
                        'Content-Type': 'application/octet-stream',
                        'Accept': 'application/json;charset=utf-8'
                    },
                    timeout=TIMEOUT_CONFIG.IMPORT_REQUEST
                )
            
            response = await retry_with_backoff(make_request)
            data = response.json()
            
            # Safely extract import status
            import_data_flows = data.get('entity', {}).get('import_data_flows', [])
            import_status = import_data_flows[0].get('status') if import_data_flows else 'unknown'
            
            logger.info('Flow import request submitted successfully', {
                'status': response.status_code,
                'import_id': data.get('metadata', {}).get('id'),
                'import_status': import_status
            })
            
            return data
            
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            message = error.response.text
            
            logger.error('Flow import request failed', {
                'status': status,
                'message': message,
                'url': str(error.request.url)
            })
            
            raise APIError(
                f'Failed to import flows: {message}',
                status,
                error.response.text
            )
        except Exception as error:
            logger.error('Request failed', {'error': str(error)})
            raise


# Made with Bob