"""
Enterprise-grade FastAPI backend for Analytics LLM Platform
Production-ready with comprehensive error handling, security, and observability
"""
from fastapi import FastAPI, HTTPException, Depends, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import traceback

# Local imports
from core.config import settings
from core.security import SecurityHeaders
from core.rate_limit import RateLimiter
from auth.auth_service import AuthService
from auth.tokens import decode_token, JWTError, create_access_token, create_refresh_token
from auth.rbac import authorize
from auth.models import User
from storage.postgres import get_db, Base, engine
from tenants.tenant_models import Tenant
from llm.router import LLMRouter
from dashboard.mcp_engine import MCPEngine
from observability.telemetry import init_telemetry
from sessions.memory_store import SessionMemoryStore
from vectorstore.vectordb import VectorStore
from ingestion.datasource import DataSourceManager
from agents.orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
rate_limiter = RateLimiter()
auth_service = AuthService()
llm_router = LLMRouter()
mcp_engine = MCPEngine()
session_store = SessionMemoryStore()
vector_store = VectorStore()
datasource_manager = DataSourceManager()
agent_orchestrator = AgentOrchestrator()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Analytics LLM Platform...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize vector store
    try:
        vector_store.initialize()
        logger.info("✅ Vector store initialized")
    except Exception as e:
        logger.warning(f"⚠️ Vector store initialization failed: {e}")
    
    yield
    
    logger.info("👋 Shutting down Analytics LLM Platform...")

# Create FastAPI app
app = FastAPI(
    title="Analytics LLM Platform",
    description="Enterprise AI-powered analytics platform with multi-tenancy and RBAC",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENV != "prod" else None,
    redoc_url="/api/redoc" if settings.ENV != "prod" else None,
)

# Initialize telemetry
init_telemetry(app)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    SecurityHeaders.add_headers(response)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENV != "prod" else "An error occurred"
        }
    )

# Dependency: Get current user from JWT
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """Extract and validate user from JWT token"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role")
        
        if not all([user_id, tenant_id, role]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {
            "id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "payload": payload
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Analytics LLM Platform API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# ==================== Authentication Routes ====================

@app.post("/api/v1/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    """Login endpoint - returns access and refresh tokens"""
    try:
        # Rate limiting
        if not rate_limiter.allow_request(f"login:{form_data.username}"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts"
            )
        
        # Authenticate user
        user = await auth_service.authenticate(
            db, 
            form_data.username, 
            form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        access_token = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role
        )
        
        refresh_token = create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "tenant_id": user.tenant_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.post("/api/v1/auth/register")
async def register(request: Dict[str, Any], db = Depends(get_db)):
    """Register a new user (self-service)"""
    try:
        email = request.get("email")
        password = request.get("password")
        tenant_id = request.get("tenant_id", "default")
        role = request.get("role", "viewer")
        tenant_name = request.get("tenant_name", "Default Tenant")

        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )

        if role not in {"viewer", "analyst", "admin"}:
            role = "viewer"

        # Ensure tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            tenant = Tenant(id=tenant_id, name=tenant_name)
            db.add(tenant)
            db.commit()

        user = await auth_service.create_user(
            db=db,
            email=email,
            password=password,
            role=role,
            tenant_id=tenant_id
        )

        return {
            "message": "User registered",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "tenant_id": user.tenant_id
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload.get("role", "viewer")
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@app.post("/api/v1/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout endpoint (token blacklisting would go here)"""
    # In production, add token to blacklist in Redis
    logger.info(f"User {current_user['id']} logged out")
    return {"message": "Logged out successfully"}

# ==================== Analytics Query Routes ====================

@app.post("/api/v1/query")
async def analytics_query(
    request_obj: Request,
    payload: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """Execute analytics query using LLM"""
    try:
        # Rate limiting
        if not rate_limiter.allow_request(f"query:{current_user['id']}"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Authorization check
        if not authorize(current_user["role"], "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Execute query with agent orchestrator
        gemini_key = request_obj.headers.get("X-GEMINI-API-KEY")

        result = await agent_orchestrator.execute_query(
            query=payload.get("query"),
            context={
                "user_id": current_user["id"],
                "tenant_id": current_user["tenant_id"],
                "role": current_user["role"],
                "gemini_api_key": gemini_key
            }
        )
        
        # Store in session memory
        session_store.add_interaction(
            user_id=current_user["id"],
            query=payload.get("query"),
            response=result
        )
        
        return {
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query execution failed"
        )

# ==================== Dashboard Routes ====================

@app.get("/api/v1/dashboard")
async def get_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get current dashboard configuration"""
    try:
        if not authorize(current_user["role"], "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Generate dashboard using MCP engine
        dashboard = await mcp_engine.generate_dashboard(
            tenant_id=current_user["tenant_id"],
            user_preferences={}
        )
        
        return {
            "dashboard": dashboard,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard generation failed"
        )

@app.post("/api/v1/dashboard/feedback")
async def dashboard_feedback(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Submit feedback for dashboard modification"""
    try:
        if not authorize(current_user["role"], "edit"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        feedback = request.get("feedback")
        
        # Process feedback with LLM
        updated_dashboard = await mcp_engine.apply_feedback(
            tenant_id=current_user["tenant_id"],
            feedback=feedback
        )
        
        return {
            "message": "Dashboard updated",
            "dashboard": updated_dashboard
        }
    except Exception as e:
        logger.error(f"Dashboard feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard feedback processing failed"
        )

# ==================== Data Source Routes ====================

@app.post("/api/v1/datasources")
async def add_datasource(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Add new data source"""
    try:
        if not authorize(current_user["role"], "edit"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        datasource = await datasource_manager.add_datasource(
            tenant_id=current_user["tenant_id"],
            config=request
        )
        
        return {
            "message": "Data source added",
            "datasource_id": datasource["id"]
        }
    except Exception as e:
        logger.error(f"Data source addition error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add data source"
        )

@app.get("/api/v1/datasources")
async def list_datasources(current_user: Dict = Depends(get_current_user)):
    """List all data sources for tenant"""
    try:
        datasources = await datasource_manager.list_datasources(
            tenant_id=current_user["tenant_id"]
        )
        
        return {"datasources": datasources}
    except Exception as e:
        logger.error(f"Data source listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list data sources"
        )

# ==================== Session Routes ====================

@app.get("/api/v1/sessions/history")
async def get_session_history(current_user: Dict = Depends(get_current_user)):
    """Get chat/query history"""
    try:
        history = session_store.get_history(user_id=current_user["id"])
        return {"history": history}
    except Exception as e:
        logger.error(f"Session history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session history"
        )

# ==================== Admin Routes ====================

@app.post("/api/v1/admin/users")
async def create_user(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new user (admin only)"""
    try:
        if not authorize(current_user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        user = await auth_service.create_user(
            db=db,
            email=request.get("email"),
            password=request.get("password"),
            role=request.get("role", "viewer"),
            tenant_id=current_user["tenant_id"]
        )
        
        return {
            "message": "User created",
            "user_id": user.id
        }
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV != "prod",
        log_level="info"
    )
