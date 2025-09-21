
"""
Document-Driven FastAPI Backend
Simplified API that takes documents and produces business reports
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import uuid
import os
from datetime import datetime
import asyncio
from enum import Enum

from dotenv import load_dotenv
load_dotenv('keys.env')

# Import the document-driven agentic system
try:
    from agentic_startup_analyst import (
        DocumentDrivenOrchestrator,
        DocumentAnalysisRequest,
        # setup_logging,
        # validate_environment
    )
    REAL_SYSTEM_AVAILABLE = True
except ImportError:
    REAL_SYSTEM_AVAILABLE = False
    print("⚠️  Document-driven system not available. Check file names and dependencies.")

# FastAPI app initialization
app = FastAPI(
    title="Document-Driven AI Startup Analyst",
    description="Upload documents, get professional investment analysis reports",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[DocumentDrivenOrchestrator] = None

# Storage for analysis results
analysis_storage: Dict[str, Dict] = {}
status_storage: Dict[str, Dict] = {}

# Analysis status enum
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING_DATA = "extracting_data"
    ANALYZING_FINANCIALS = "analyzing_financials" 
    ASSESSING_RISKS = "assessing_risks"
    ANALYZING_MARKET = "analyzing_market"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"

# Simplified request models (just documents + optional info)
class DocumentAnalysisRequest(BaseModel):
    company_name: Optional[str] = None  # Optional hint
    documents: List[str]  # File paths to uploaded documents
    additional_writeup: Optional[str] = None  # Optional additional information

class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    progress: float
    current_step: str
    estimated_completion: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the document-driven AI system on startup"""
    global orchestrator

    print("🚀 Initializing Document-Driven AI Startup Analyst...")

    if not REAL_SYSTEM_AVAILABLE:
        print("❌ Document-driven system not available - check imports")
        return

    try:
        # Setup logging
        # setup_logging()

        # Get Gemini API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            print("❌ GEMINI_API_KEY environment variable not set")
            return

        # Initialize orchestrator
        orchestrator = DocumentDrivenOrchestrator(gemini_api_key)
        print("✅ Document-driven AI orchestrator initialized successfully!")

    except Exception as e:
        print(f"❌ Failed to initialize document-driven system: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check for document-driven system"""

    if orchestrator:
        try:
            health_status = orchestrator.get_system_health()
            return health_status
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Document-driven AI system health check failed"
            }
    else:
        return {
            "status": "not_initialized",
            "message": "Document-driven AI system not available",
            "required": "GEMINI_API_KEY environment variable"
        }

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for analysis"""

    # Check file type - support more document types
    allowed_extensions = {'.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx'}
    file_extension = os.path.splitext(file.filename.lower())[1]

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Supported: {', '.join(allowed_extensions)}"
        )

    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Save file to disk
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file_id}_{file.filename}"

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(contents),
            "upload_timestamp": datetime.now().isoformat(),
            "status": "uploaded_successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/v1/analyze-documents")
async def analyze_documents(
    background_tasks: BackgroundTasks,
    company_name: Optional[str] = Form(None),
    additional_writeup: Optional[str] = Form(None),
    document_paths: str = Form(...)  # JSON string of document paths
):
    """
    Start document-driven analysis
    Input: Documents + optional company name/writeup
    Output: Professional business report
    """

    try:
        # Parse document paths
        try:
            documents = json.loads(document_paths) if document_paths else []
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid document_paths JSON format")

        if not documents:
            raise HTTPException(status_code=400, detail="At least one document is required")

        # Verify documents exist
        missing_docs = [doc for doc in documents if not os.path.exists(doc)]
        if missing_docs:
            raise HTTPException(status_code=400, detail=f"Documents not found: {missing_docs}")

        # Generate analysis ID
        analysis_id = str(uuid.uuid4())

        # Initialize status
        status_storage[analysis_id] = {
            "status": AnalysisStatus.PENDING,
            "progress": 0.0,
            "current_step": "Initializing document analysis...",
            "start_time": datetime.now(),
            "estimated_completion": None
        }

        # Create analysis request
        analysis_request = DocumentAnalysisRequest(
            company_name=company_name,
            documents=documents,
            additional_writeup=additional_writeup
        )

        # Start analysis in background
        if orchestrator:
            background_tasks.add_task(run_document_driven_analysis, analysis_id, analysis_request)
        else:
            raise HTTPException(status_code=503, detail="Document-driven AI system not available")

        return {
            "analysis_id": analysis_id,
            "status": "started",
            "message": f"Document analysis initiated for {len(documents)} documents",
            "estimated_duration_minutes": 2,
            "status_endpoint": f"/api/v1/analysis/{analysis_id}/status"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

async def run_document_driven_analysis(analysis_id: str, request: DocumentAnalysisRequest):
    """Run the complete document-driven analysis pipeline"""

    try:
        print(f"🚀 Starting document-driven analysis for {analysis_id}")

        # Step 1: Document extraction
        status_storage[analysis_id].update({
            "status": AnalysisStatus.EXTRACTING_DATA,
            "progress": 15.0,
            "current_step": "Extracting company data from documents..."
        })
        await asyncio.sleep(1)  # Small delay for UI

        # Step 2: Financial analysis
        status_storage[analysis_id].update({
            "status": AnalysisStatus.ANALYZING_FINANCIALS,
            "progress": 35.0,
            "current_step": "Analyzing financial metrics and health..."
        })
        await asyncio.sleep(1)

        # Step 3: Risk assessment
        status_storage[analysis_id].update({
            "status": AnalysisStatus.ASSESSING_RISKS,
            "progress": 55.0,
            "current_step": "Assessing investment risks and red flags..."
        })
        await asyncio.sleep(1)

        # Step 4: Market analysis
        status_storage[analysis_id].update({
            "status": AnalysisStatus.ANALYZING_MARKET,
            "progress": 75.0,
            "current_step": "Analyzing market opportunity and competition..."
        })
        await asyncio.sleep(1)

        # Step 5: Report generation
        status_storage[analysis_id].update({
            "status": AnalysisStatus.GENERATING_REPORT,
            "progress": 90.0,
            "current_step": "Generating comprehensive business report..."
        })

        # Run the actual analysis
        result = await orchestrator.analyze_startup_from_documents(request)

        # Store results
        analysis_storage[analysis_id] = result

        # Mark as completed
        status_storage[analysis_id].update({
            "status": AnalysisStatus.COMPLETED,
            "progress": 100.0,
            "current_step": "Business report generated successfully!",
            "completion_time": datetime.now()
        })

        print(f"✅ Document-driven analysis completed for {analysis_id}")

    except Exception as e:
        print(f"❌ Document analysis failed for {analysis_id}: {str(e)}")

        # Mark as failed
        status_storage[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "current_step": f"Analysis failed: {str(e)}",
            "error": str(e)
        })

@app.get("/api/v1/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get current status of document analysis"""

    if analysis_id not in status_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")

    status = status_storage[analysis_id]

    return {
        "analysis_id": analysis_id,
        "status": status["status"],
        "progress": status["progress"],
        "current_step": status["current_step"],
        "start_time": status["start_time"].isoformat(),
        "completion_time": status.get("completion_time", {}).isoformat() if status.get("completion_time") else None,
        "error": status.get("error")
    }

@app.get("/api/v1/analysis/{analysis_id}/report")
async def get_business_report(analysis_id: str):
    """Get completed business report"""

    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Business report not found")

    if status_storage.get(analysis_id, {}).get("status") != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    return analysis_storage[analysis_id]

@app.get("/api/v1/analysis/{analysis_id}/summary")  
async def get_analysis_summary(analysis_id: str):
    """Get executive summary of the analysis"""

    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report = analysis_storage[analysis_id]

    # Extract key information for quick preview
    executive_summary = report.get("executive_summary", {})

    return {
        "analysis_id": analysis_id,
        "company_name": report.get("report_metadata", {}).get("company_name"),
        "overall_score": executive_summary.get("overall_score"),
        "investment_recommendation": executive_summary.get("investment_recommendation"),
        "key_highlights": executive_summary.get("key_highlights", [])[:3],
        "critical_concerns": executive_summary.get("critical_concerns", [])[:2],
        "analysis_date": report.get("report_metadata", {}).get("analysis_date")
    }

# Additional utility endpoints
@app.get("/api/v1/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "supported_formats": [
            {
                "extension": ".pdf",
                "description": "Portable Document Format",
                "recommended": True
            },
            {
                "extension": ".pptx",
                "description": "PowerPoint Presentation",
                "recommended": True
            },
            {
                "extension": ".docx", 
                "description": "Word Document",
                "recommended": True
            },
            {
                "extension": ".txt",
                "description": "Plain Text",
                "recommended": False
            },
            {
                "extension": ".md",
                "description": "Markdown",
                "recommended": False
            }
        ],
        "recommendations": [
            "Upload pitch decks as PDF or PPTX for best results",
            "Include financial statements and business plans",
            "Multiple documents provide more comprehensive analysis"
        ]
    }

@app.delete("/api/v1/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete analysis results and free up storage"""

    deleted_items = []

    if analysis_id in analysis_storage:
        del analysis_storage[analysis_id]
        deleted_items.append("analysis_results")

    if analysis_id in status_storage:
        del status_storage[analysis_id]
        deleted_items.append("status_data")

    if not deleted_items:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "message": f"Analysis {analysis_id} deleted successfully",
        "deleted_items": deleted_items
    }

@app.get("/api/v1/analyses")
async def list_analyses():
    """List all analyses (for debugging/admin)"""

    analyses = []

    for analysis_id in analysis_storage.keys():
        status = status_storage.get(analysis_id, {})
        report = analysis_storage.get(analysis_id, {})

        analyses.append({
            "analysis_id": analysis_id,
            "status": status.get("status"),
            "company_name": report.get("report_metadata", {}).get("company_name"),
            "start_time": status.get("start_time", {}).isoformat() if status.get("start_time") else None,
            "completion_time": status.get("completion_time", {}).isoformat() if status.get("completion_time") else None
        })

    return {
        "total_analyses": len(analyses),
        "analyses": analyses
    }

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Document-Driven AI Startup Analyst...")
    print("📊 Just upload documents - get professional business reports!")
    print("📖 API Documentation: http://localhost:8000/docs")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
