"""
Security middleware for API authentication
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

security = HTTPBearer()

class APIKeyValidator:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.enabled = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
    
    async def validate(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[str]:
        """Validate API key if authentication is enabled"""
        if not self.enabled:
            return "auth_disabled"
        
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key not configured"
            )
        
        if credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return credentials.credentials

# Global validator instance
api_key_validator = APIKeyValidator()

# Dependency for protected endpoints
async def require_api_key(api_key: str = Security(api_key_validator.validate)):
    """Dependency to require API key for protected endpoints"""
    return api_key