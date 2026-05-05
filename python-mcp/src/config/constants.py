"""
Configuration constants for DataStage MCP Server - Simplified Version
"""

import os
from typing import Optional

# Environment variables
class ENV:
    CPD_URL = os.getenv('CPD_URL', '')
    CPD_USERNAME = os.getenv('CPD_USERNAME', '')
    CPD_PASSWORD = os.getenv('CPD_PASSWORD', '')
    CPD_PROJECT_ID = os.getenv('CPD_PROJECT_ID', '')
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')


# API endpoints
class API_ENDPOINTS:
    # Authentication
    AUTHORIZE = '/icp4d-api/v1/authorize'
    
    # Projects API - v2
    @staticmethod
    def PROJECTS(limit: int = 100, bss_account_id: Optional[str] = None) -> str:
        params = f'limit={limit}'
        if bss_account_id:
            params += f'&bss_account_id={bss_account_id}'
        return f'/v2/projects?{params}'
    
    # Jobs API - v2 (Runtime jobs with correct IDs for runs)
    @staticmethod
    def JOBS(project_id: str) -> str:
        return f'/v2/jobs?project_id={project_id}'
    
    @staticmethod
    def JOB_RUNS(job_id: str, project_id: str) -> str:
        return f'/v2/jobs/{job_id}/runs?project_id={project_id}'
    
    @staticmethod
    def RUN_JOB(job_id: str, project_id: str) -> str:
        return f'/v2/jobs/{job_id}/runs?project_id={project_id}&userfs=false'
    
    @staticmethod
    def JOB_RUN_LOGS(job_id: str, run_id: str, project_id: str) -> str:
        return f'/v2/jobs/{job_id}/runs/{run_id}/logs?project_id={project_id}&userfs=false'
    
    # DataStage Flows (Jobs) - v3 API (Design-time, different IDs)
    @staticmethod
    def FLOWS(project_id: str) -> str:
        return f'/data_intg/v3/data_intg_flows?project_id={project_id}'
    
    @staticmethod
    def FLOW_DETAILS(flow_id: str, project_id: str) -> str:
        return f'/data_intg/v3/data_intg_flows/{flow_id}?project_id={project_id}'
    
    # Flow Export/Import (using migration API)
    @staticmethod
    def EXPORT_FLOWS(project_id: str) -> str:
        return f'/data_intg/v3/migration/zip_exports?project_id={project_id}'
    
    @staticmethod
    def IMPORT_FLOWS(project_id: str) -> str:
        return f'/data_intg/v3/migration/zip_imports?project_id={project_id}'
    
    # Flow Compilation
    @staticmethod
    def COMPILE_FLOW(flow_id: str, project_id: str) -> str:
        return f'/data_intg/v3/ds_codegen/compile/{flow_id}?project_id={project_id}'


# Cache keys
class CACHE_KEYS:
    AUTH_TOKEN = 'auth_token'
    PROJECT_ID = 'project_id'


# Retry configuration
class RETRY_CONFIG:
    MAX_RETRIES = 3
    INITIAL_DELAY = 1.0  # 1 second
    MAX_DELAY = 10.0  # 10 seconds
    BACKOFF_MULTIPLIER = 2


# Timeout configuration (in seconds)
class TIMEOUT_CONFIG:
    API_REQUEST = 30.0  # 30 seconds
    AUTH_REQUEST = 10.0  # 10 seconds
    IMPORT_REQUEST = 120.0  # 120 seconds (2 minutes) for import operations


# Made with Bob