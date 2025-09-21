
"""
FastAPI Application for AI-Powered Startup Analyst Platform
Google Cloud Integration with Agentic AI System
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
from datetime import datetime
import uuid

# Import our agentic AI system
from agentic_startup_analyst import StartupAnalystOrchestrator, AnalysisRequest

# Initialize FastAPI app
app = FastAPI(
    title="AI Startup Analyst Platform",
    description="Agentic AI system for comprehensive startup evaluation",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI orchestrator
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
ai_orchestrator = StartupAnalystOrchestrator(GEMINI_API_KEY)

# Pydantic models for API
class CompanyInfo(BaseModel):
    name: str
    sector: str
    stage: str
    funding_request: float
    description: Optional[str] = None

class FinancialData(BaseModel):
    monthly_revenue: Optional[float] = None
    burn_rate: Optional[float] = None
    cash_balance: Optional[float] = None
    employees: Optional[int] = None
    customers: Optional[int] = None
    gross_margin: Optional[float] = None

class AnalysisRequestAPI(BaseModel):
    company_info: CompanyInfo
    financial_data: FinancialData
    documents: Optional[List[str]] = []
    additional_info: Optional[Dict[str, Any]] = {}

class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str
    progress: float
    current_step: str
    estimated_completion: Optional[datetime] = None

# In-memory storage for demo (use Firebase Firestore in production)
analysis_storage = {}
status_storage = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Startup Analyst Platform - Agentic AI System",
        "status": "operational",
        "version": "1.0.0",
        "agents": 5,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_status": {
            "document_intelligence": "ready",
            "financial_analysis": "ready", 
            "risk_assessment": "ready",
            "market_intelligence": "ready",
            "synthesis_reporting": "ready"
        },
        "google_cloud_services": {
            "gemini_api": "connected",
            "cloud_vision": "ready",
            "bigquery": "ready",
            "firestore": "ready"
        }
    }

@app.post("/api/v1/analyze")
async def analyze_startup(
    analysis_request: AnalysisRequestAPI,
    background_tasks: BackgroundTasks
):
    """
    Start comprehensive startup analysis using agentic AI system
    """

    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())

    # Initialize status tracking
    status_storage[analysis_id] = AnalysisStatus(
        analysis_id=analysis_id,
        status="initiated",
        progress=0.0,
        current_step="Initializing analysis"
    )

    # Convert API request to internal format
    internal_request = AnalysisRequest(
        company_name=analysis_request.company_info.name,
        documents=analysis_request.documents,
        financial_data=analysis_request.financial_data.dict(),
        metadata={
            "sector": analysis_request.company_info.sector,
            "stage": analysis_request.company_info.stage,
            "funding_request": analysis_request.company_info.funding_request,
            **analysis_request.additional_info
        }
    )

    # Start analysis in background
    background_tasks.add_task(run_analysis, analysis_id, internal_request)

    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": f"Analysis initiated for {analysis_request.company_info.name}",
        "estimated_duration_minutes": 3,
        "status_endpoint": f"/api/v1/analysis/{analysis_id}/status"
    }

async def run_analysis(analysis_id: str, request: AnalysisRequest):
    """
    Background task to run the complete analysis
    """

    try:
        # Update status: Document Intelligence
        status_storage[analysis_id].status = "processing"
        status_storage[analysis_id].progress = 20.0
        status_storage[analysis_id].current_step = "Document Intelligence Agent"

        # Update status: Financial Analysis  
        await asyncio.sleep(1)  # Simulate processing time
        status_storage[analysis_id].progress = 40.0
        status_storage[analysis_id].current_step = "Financial Analysis Agent"

        # Update status: Risk Assessment
        await asyncio.sleep(1)
        status_storage[analysis_id].progress = 60.0
        status_storage[analysis_id].current_step = "Risk Assessment Agent"

        # Update status: Market Intelligence
        await asyncio.sleep(1)
        status_storage[analysis_id].progress = 80.0
        status_storage[analysis_id].current_step = "Market Intelligence Agent"

        # Update status: Synthesis
        await asyncio.sleep(1)
        status_storage[analysis_id].progress = 90.0
        status_storage[analysis_id].current_step = "Synthesis & Reporting Agent"

        # Run the actual analysis
        result = await ai_orchestrator.analyze_startup(request)

        # Store results
        analysis_storage[analysis_id] = result

        # Mark as completed
        status_storage[analysis_id].status = "completed"
        status_storage[analysis_id].progress = 100.0
        status_storage[analysis_id].current_step = "Analysis complete"

    except Exception as e:
        status_storage[analysis_id].status = "failed"
        status_storage[analysis_id].current_step = f"Error: {str(e)}"

@app.get("/api/v1/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """
    Get analysis status and progress
    """

    if analysis_id not in status_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")

    status = status_storage[analysis_id]

    response = {
        "analysis_id": analysis_id,
        "status": status.status,
        "progress": status.progress,
        "current_step": status.current_step
    }

    # Add results if completed
    if status.status == "completed" and analysis_id in analysis_storage:
        response["results_available"] = True
        response["results_endpoint"] = f"/api/v1/analysis/{analysis_id}/results"

    return response

@app.get("/api/v1/analysis/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """
    Get complete analysis results
    """

    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis results not found")

    if status_storage[analysis_id].status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    return analysis_storage[analysis_id]

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process startup documents
    """

    if not file.filename.lower().endswith(('.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # In production: upload to Google Cloud Storage
    # For now, simulate upload

    file_id = str(uuid.uuid4())

    return {
        "file_id": file_id,
        "filename": file.filename,
        "status": "uploaded",
        "message": "Document uploaded and ready for analysis",
        "supported_analysis": [
            "pitch_deck_analysis",
            "financial_statement_analysis", 
            "market_research_validation"
        ]
    }

@app.get("/api/v1/benchmarks/{sector}")
async def get_sector_benchmarks(sector: str):
    """
    Get sector benchmark data from BigQuery
    """

    # In production: Query BigQuery for real benchmark data
    benchmark_data = {
        "sector": sector,
        "metrics": {
            "median_burn_rate": 75000,
            "median_growth_rate_mom": 12.5,
            "median_gross_margin": 72.0,
            "median_cac_payback_months": 16,
            "median_ltv_cac_ratio": 3.8,
            "median_runway_months": 14
        },
        "sample_size": 247,
        "last_updated": datetime.now().isoformat()
    }

    return benchmark_data

@app.get("/api/v1/companies/{company_id}/risk-profile")
async def get_risk_profile(company_id: str):
    """
    Get detailed risk assessment for a company
    """

    # Mock risk profile data
    risk_profile = {
        "company_id": company_id,
        "overall_risk_score": 35.5,
        "risk_level": "Medium-Low",
        "risk_breakdown": {
            "financial_risk": 25.0,
            "market_risk": 40.0,
            "team_risk": 15.0,
            "technology_risk": 20.0,
            "competitive_risk": 45.0,
            "regulatory_risk": 10.0
        },
        "critical_flags": [
            "Customer concentration risk exceeds 60%",
            "Market size validation needed"
        ],
        "mitigation_strategies": [
            "Diversify customer base through targeted acquisition",
            "Conduct independent market research validation"
        ]
    }

    return risk_profile

@app.get("/api/v1/market-intelligence/{sector}")
async def get_market_intelligence(sector: str):
    """
    Get real-time market intelligence
    """

    # Mock market intelligence data
    intelligence = {
        "sector": sector,
        "market_data": {
            "growth_rate_cagr": 23.0,
            "market_size_billions": 15.2,
            "funding_activity_12m": 180000000,
            "new_entrants_12m": 15,
            "exits_12m": 3
        },
        "competitive_landscape": {
            "top_competitors": [
                {"name": "Competitor A", "funding": "$50M", "valuation": "$200M"},
                {"name": "Competitor B", "funding": "$75M", "valuation": "$350M"},
                {"name": "Competitor C", "funding": "$30M", "valuation": "$150M"}
            ],
            "market_concentration": 45.0,
            "barriers_to_entry": "Medium"
        },
        "trends": [
            "Increasing adoption of AI-powered solutions",
            "Growing enterprise customer segment",
            "Regulatory changes favoring innovation"
        ],
        "timestamp": datetime.now().isoformat()
    }

    return intelligence

@app.websocket("/api/v1/analysis/{analysis_id}/live")
async def websocket_analysis_updates(websocket, analysis_id: str):
    """
    WebSocket endpoint for real-time analysis updates
    """
    await websocket.accept()

    # Send real-time updates during analysis
    while True:
        if analysis_id in status_storage:
            status = status_storage[analysis_id]
            await websocket.send_json({
                "analysis_id": analysis_id,
                "status": status.status,
                "progress": status.progress,
                "current_step": status.current_step,
                "timestamp": datetime.now().isoformat()
            })

            if status.status in ["completed", "failed"]:
                break

        await asyncio.sleep(1)

    await websocket.close()

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found", "status": "error"}
    )

@app.exception_handler(500) 
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "status": "error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
