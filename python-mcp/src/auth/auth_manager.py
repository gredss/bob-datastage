"""
Authentication Manager for Cloud Pak for Data
Handles token generation, caching, and refresh
"""

import httpx
import time
from typing import Optional, Dict, Any
from ..config.constants import ENV, API_ENDPOINTS, CACHE_KEYS
from ..utils.cache import SimpleCache
from ..utils.logger import logger


class AuthenticationError(Exception):
    """Authentication error"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.details = details


class AuthManager:
    """Manages authentication with Cloud Pak for Data"""
    
    def __init__(self):
        self.cache = SimpleCache()
        self.token_expiration: float = 0
        self.base_url = ENV.CPD_URL
    
    async def get_token(self) -> str:
        """Get a valid bearer token, refreshing if necessary"""
        # Check if we have a cached valid token
        cached_token = self.cache.get(CACHE_KEYS.AUTH_TOKEN)
        if cached_token and self._is_token_valid():
            logger.debug('Using cached authentication token')
            return cached_token
        
        # Authenticate to get a new token
        logger.info('Authenticating with Cloud Pak for Data')
        return await self._authenticate()
    
    async def _authenticate(self) -> str:
        """Authenticate with CPD and get a bearer token"""
        try:
            auth_payload = self._build_auth_payload()
            
            logger.debug('Sending authentication request to CPD')
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f'{self.base_url}{API_ENDPOINTS.AUTHORIZE}',
                    json=auth_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            
            token = data['token']
            expires_in = data.get('expires_in', 3600)  # Default to 1 hour if not provided
            expiration = data.get('expiration', time.time() + expires_in)
            
            # Cache the token
            self.token_expiration = expiration
            # Use max to ensure TTL is at least 60 seconds
            cache_ttl = max(expires_in - 60, 60)
            self.cache.set(CACHE_KEYS.AUTH_TOKEN, token, cache_ttl)
            
            logger.info('Successfully authenticated with CPD')
            return token
            
        except httpx.HTTPStatusError as error:
            message = error.response.text
            status_code = error.response.status_code
            
            logger.error('Authentication failed', {'message': message, 'status_code': status_code})
            
            raise AuthenticationError(
                f'Failed to authenticate with CPD: {message}',
                {'status_code': status_code, 'original_error': str(error)}
            )
        except Exception as error:
            logger.error('Authentication failed', {'error': str(error)})
            raise AuthenticationError(f'Failed to authenticate with CPD: {str(error)}')
    
    def _build_auth_payload(self) -> Dict[str, str]:
        """Build authentication payload based on available credentials"""
        # Use username/password authentication
        if ENV.CPD_USERNAME and ENV.CPD_PASSWORD:
            logger.debug('Using username/password authentication')
            return {
                'username': ENV.CPD_USERNAME,
                'password': ENV.CPD_PASSWORD,
            }
        
        raise AuthenticationError(
            'No authentication credentials provided. Set CPD_USERNAME and CPD_PASSWORD environment variables.'
        )
    
    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid"""
        if self.token_expiration == 0:
            return False
        
        # Consider token invalid if it expires in less than 60 seconds
        now = time.time()
        buffer_time = 60  # 60 seconds
        return self.token_expiration > now + buffer_time
    
    async def refresh_token(self) -> str:
        """Force token refresh"""
        logger.info('Forcing token refresh')
        self.cache.delete(CACHE_KEYS.AUTH_TOKEN)
        self.token_expiration = 0
        return await self._authenticate()
    
    def clear_cache(self) -> None:
        """Clear cached authentication data"""
        logger.debug('Clearing authentication cache')
        self.cache.delete(CACHE_KEYS.AUTH_TOKEN)
        self.token_expiration = 0
    
    def validate_configuration(self) -> None:
        """Validate that CPD URL is configured"""
        if not ENV.CPD_URL:
            raise AuthenticationError('CPD_URL environment variable is required')
        
        if not ENV.CPD_USERNAME or not ENV.CPD_PASSWORD:
            raise AuthenticationError('CPD_USERNAME and CPD_PASSWORD must be provided')


# Made with Bob