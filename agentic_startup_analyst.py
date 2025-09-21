
"""
Document-Driven AI Startup Analyst Platform - COMPLETE FIXED VERSION
All agents working with proper error handling
"""

import asyncio
import json
import os
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import traceback

# Simplified Google AI imports - GEMINI ONLY
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Google Generative AI (Gemini) imported successfully")
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ Google Generative AI not available. Install: pip install google-generativeai")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentAnalysisRequest:
    """Simplified request structure - just documents and optional info"""
    company_name: Optional[str]
    documents: List[str]
    additional_writeup: Optional[str] = None
    analysis_timestamp: datetime = datetime.now()

@dataclass
class ExtractedCompanyData:
    """Structure for data extracted from documents"""
    # Company basics
    company_name: Optional[str] = None
    sector: Optional[str] = None
    stage: Optional[str] = None
    location: Optional[str] = None
    founded_date: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    # Funding information
    funding_request: Optional[float] = None
    previous_funding: Optional[str] = None
    valuation: Optional[str] = None

    # Financial data
    monthly_revenue: Optional[float] = None
    annual_revenue: Optional[float] = None
    burn_rate: Optional[float] = None
    cash_balance: Optional[float] = None
    gross_margin: Optional[float] = None

    # Business metrics
    customers: Optional[int] = None
    employees: Optional[int] = None
    customer_acquisition_cost: Optional[float] = None
    lifetime_value: Optional[float] = None
    retention_rate: Optional[float] = None
    growth_rate: Optional[float] = None

    # Team information
    founders: Optional[List[str]] = None
    key_team: Optional[List[str]] = None
    advisors: Optional[List[str]] = None

    # Market and product
    target_market: Optional[str] = None
    product_description: Optional[str] = None
    competitive_advantages: Optional[List[str]] = None
    partnerships: Optional[List[str]] = None

    # Other
    regulatory_status: Optional[str] = None
    ip_portfolio: Optional[str] = None

    # Confidence scores for each extracted field
    extraction_confidence: Dict[str, float] = None

@dataclass
class AgentResponse:
    """Standard response format for all agents"""
    agent_name: str
    timestamp: datetime
    confidence_score: float
    findings: List[str]
    analysis: Dict[str, Any]
    recommendations: List[str]
    flags: List[str]
    data_completeness: float

class BaseAgent:
    """Base class for all AI agents - GEMINI ONLY VERSION"""

    def __init__(self, agent_name: str, gemini_api_key: str):
        self.agent_name = agent_name
        self.api_key = gemini_api_key
        self.confidence_threshold = 0.7

        if not GEMINI_AVAILABLE:
            logger.error("❌ Gemini not available!")
            self.gemini_model = None
            return

        # Configure ONLY Gemini (no Cloud Vision)
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info(f"✅ {agent_name} initialized with Gemini Pro (API key only)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini for {agent_name}: {e}")
                self.gemini_model = None
        else:
            logger.error(f"❌ No Gemini API key provided for {agent_name}")
            self.gemini_model = None

    def log_activity(self, message: str):
        """Log agent activity"""
        logger.info(f"[{self.agent_name}] {message}")

    async def call_gemini(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Make API call to Gemini with retries"""
        if not self.gemini_model:
            logger.error("❌ Gemini model not initialized")
            return None

        for attempt in range(max_retries):
            try:
                self.log_activity(f"Making Gemini API call (attempt {attempt + 1})")
                response = self.gemini_model.generate_content(prompt)

                if response and response.text:
                    self.log_activity("✅ Gemini API call successful")
                    return response.text
                else:
                    self.log_activity("⚠️ Empty response from Gemini")

            except Exception as e:
                self.log_activity(f"❌ Gemini API error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to get response from Gemini after {max_retries} attempts")

        return None

    def safe_format_currency(self, value: Optional[float]) -> str:
        """Safely format currency values, handling None"""
        if value is None:
            return "Unknown"
        try:
            return f"${value:,.0f}"
        except:
            return "Unknown"

    def safe_format_number(self, value: Optional[float]) -> str:
        """Safely format numbers, handling None"""
        if value is None:
            return "Unknown"
        try:
            return f"{value:,.0f}"
        except:
            return "Unknown"

class DocumentExtractionAgent(BaseAgent):
    """Document Extraction Agent - Uses only Gemini API"""

    def __init__(self, gemini_api_key: str):
        super().__init__("Document Extraction Agent", gemini_api_key)
        self.log_activity("Initialized with Gemini API only (no Cloud Vision required)")

    async def extract_company_data(self, request: DocumentAnalysisRequest) -> ExtractedCompanyData:
        """Extract comprehensive company data from all documents using ONLY Gemini"""
        self.log_activity("Starting document extraction with Gemini API only")

        try:
            # Extract raw content from all documents (text-based)
            all_content = await self._extract_text_content_simple(request.documents)

            # Add additional writeup if provided
            if request.additional_writeup:
                all_content += f"\n\n=== ADDITIONAL INFORMATION ===\n{request.additional_writeup}"

            # Use Gemini AI to extract structured data
            extracted_data = await self._extract_structured_data_with_gemini(all_content, request.company_name)

            self.log_activity(f"✅ Extracted data for {extracted_data.company_name or 'Unknown Company'}")
            return extracted_data

        except Exception as e:
            self.log_activity(f"❌ Error in document extraction: {str(e)}")
            return ExtractedCompanyData()

    async def _extract_text_content_simple(self, documents: List[str]) -> str:
        """Extract text content from documents using simple text reading"""
        all_content = []

        for doc_path in documents:
            try:
                if os.path.exists(doc_path):
                    content = self._extract_text_from_file(doc_path)
                    if content:
                        all_content.append(f"=== DOCUMENT: {os.path.basename(doc_path)} ===\n{content}\n")
                        self.log_activity(f"✅ Extracted content from {doc_path}")
                    else:
                        self.log_activity(f"⚠️ No content extracted from {doc_path}")
                else:
                    self.log_activity(f"⚠️ Document not found: {doc_path}")
            except Exception as e:
                self.log_activity(f"❌ Error reading {doc_path}: {e}")

        return "\n".join(all_content) if all_content else "No document content available"

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        try:
            file_ext = os.path.splitext(file_path.lower())[1]

            if file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

            elif file_ext == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    self.log_activity("⚠️ python-docx not installed, reading as text")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()

            elif file_ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    self.log_activity("⚠️ PyPDF2 not installed, reading as text")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()

            else:
                # Fall back to reading as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

        except Exception as e:
            self.log_activity(f"❌ Error extracting text from {file_path}: {e}")
            return ""

    async def _extract_structured_data_with_gemini(self, content: str, company_hint: Optional[str]) -> ExtractedCompanyData:
        """Use ONLY Gemini to extract structured company data"""

        content_limited = content[:12000] if len(content) > 12000 else content

        prompt = f"""
        Extract key startup information from these documents and respond in JSON format:

        DOCUMENTS:
        {content_limited}

        Company hint: {company_hint or "Not specified"}

        Extract information and return JSON with these fields (use null for missing data):

        {{
          "company_name": "Full company name",
          "sector": "Industry sector",
          "stage": "Funding stage",
          "location": "Company location", 
          "founded_date": "Founding date",
          "website": "Website URL",
          "description": "Company description",
          "funding_request": 1000000,
          "monthly_revenue": 50000,
          "annual_revenue": 600000,
          "burn_rate": 40000,
          "cash_balance": 500000,
          "gross_margin": 75.0,
          "customers": 25,
          "employees": 15,
          "customer_acquisition_cost": 500,
          "lifetime_value": 5000,
          "retention_rate": 85.0,
          "growth_rate": 10.0,
          "founders": ["Name 1", "Name 2"],
          "key_team": ["Person 1 (Title)", "Person 2 (Title)"],
          "target_market": "Target market description",
          "product_description": "Product description",
          "competitive_advantages": ["Advantage 1", "Advantage 2"]
        }}

        Return only valid JSON, no additional text.
        """

        response = await self.call_gemini(prompt)

        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    data_dict = json.loads(json_match.group())

                    extracted = ExtractedCompanyData()

                    # Basic info
                    extracted.company_name = data_dict.get('company_name')
                    extracted.sector = data_dict.get('sector')
                    extracted.stage = data_dict.get('stage')
                    extracted.location = data_dict.get('location')
                    extracted.founded_date = data_dict.get('founded_date')
                    extracted.website = data_dict.get('website')
                    extracted.description = data_dict.get('description')

                    # Funding
                    extracted.funding_request = self._safe_float(data_dict.get('funding_request'))

                    # Financials
                    extracted.monthly_revenue = self._safe_float(data_dict.get('monthly_revenue'))
                    extracted.annual_revenue = self._safe_float(data_dict.get('annual_revenue'))
                    extracted.burn_rate = self._safe_float(data_dict.get('burn_rate'))
                    extracted.cash_balance = self._safe_float(data_dict.get('cash_balance'))
                    extracted.gross_margin = self._safe_float(data_dict.get('gross_margin'))

                    # Metrics
                    extracted.customers = self._safe_int(data_dict.get('customers'))
                    extracted.employees = self._safe_int(data_dict.get('employees'))
                    extracted.customer_acquisition_cost = self._safe_float(data_dict.get('customer_acquisition_cost'))
                    extracted.lifetime_value = self._safe_float(data_dict.get('lifetime_value'))
                    extracted.retention_rate = self._safe_float(data_dict.get('retention_rate'))
                    extracted.growth_rate = self._safe_float(data_dict.get('growth_rate'))

                    # Lists
                    extracted.founders = data_dict.get('founders') if isinstance(data_dict.get('founders'), list) else None
                    extracted.key_team = data_dict.get('key_team') if isinstance(data_dict.get('key_team'), list) else None
                    extracted.competitive_advantages = data_dict.get('competitive_advantages') if isinstance(data_dict.get('competitive_advantages'), list) else None

                    # Market
                    extracted.target_market = data_dict.get('target_market')
                    extracted.product_description = data_dict.get('product_description')

                    # Confidence
                    extracted.extraction_confidence = self._calculate_extraction_confidence(extracted)

                    self.log_activity("✅ Successfully extracted structured data using Gemini API")
                    return extracted

            except Exception as e:
                self.log_activity(f"❌ Error parsing extracted data: {e}")

        # Fallback
        self.log_activity("⚠️ Using fallback extraction")
        return ExtractedCompanyData(
            company_name=company_hint,
            extraction_confidence={"overall": 0.1}
        )

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                clean_value = re.sub(r'[,$%]', '', str(value))
                return float(clean_value) if clean_value else None
        except (ValueError, TypeError):
            pass
        return None

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        if value is None:
            return None
        try:
            if isinstance(value, int):
                return value
            if isinstance(value, (float, str)):
                return int(float(value))
        except (ValueError, TypeError):
            pass
        return None

    def _calculate_extraction_confidence(self, data: ExtractedCompanyData) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        total_fields = 0
        filled_fields = 0

        for field_name, field_value in asdict(data).items():
            if field_name == 'extraction_confidence':
                continue
            total_fields += 1
            if field_value is not None:
                filled_fields += 1

        overall_confidence = filled_fields / total_fields if total_fields > 0 else 0
        return {
            'overall': overall_confidence,
            'completeness': filled_fields / total_fields if total_fields > 0 else 0
        }

class EnhancedFinancialAnalysisAgent(BaseAgent):
    """Financial Analysis Agent - Fixed version"""

    def __init__(self, gemini_api_key: str):
        super().__init__("Financial Analysis Agent", gemini_api_key)

    async def analyze_extracted_data(self, extracted_data: ExtractedCompanyData) -> AgentResponse:
        """Analyze financial health based on extracted data"""
        self.log_activity(f"Analyzing financials for {extracted_data.company_name or 'Unknown Company'}")

        try:
            # Calculate available financial metrics
            financial_metrics = self._calculate_available_metrics(extracted_data)

            # Generate AI insights based on available data
            insights = await self._generate_financial_insights(extracted_data, financial_metrics)

            # Generate recommendations
            recommendations = await self._generate_financial_recommendations(extracted_data, financial_metrics)

            # Detect financial red flags
            flags = self._detect_financial_flags(extracted_data, financial_metrics)

            # Calculate completeness and confidence
            data_completeness = self._calculate_financial_completeness(extracted_data)
            confidence = self._calculate_financial_confidence(extracted_data, financial_metrics)

            return AgentResponse(
                agent_name=self.agent_name,
                timestamp=datetime.now(),
                confidence_score=confidence,
                findings=insights,
                analysis=financial_metrics,
                recommendations=recommendations,
                flags=flags,
                data_completeness=data_completeness
            )

        except Exception as e:
            self.log_activity(f"❌ Error in financial analysis: {str(e)}")
            return self._create_error_response(str(e))

    def _calculate_available_metrics(self, data: ExtractedCompanyData) -> Dict[str, Any]:
        """Calculate financial metrics based on available extracted data"""
        metrics = {}

        try:
            # Basic metrics
            if data.monthly_revenue:
                metrics['monthly_revenue'] = data.monthly_revenue
                metrics['annual_run_rate'] = data.monthly_revenue * 12

            if data.annual_revenue:
                metrics['annual_revenue'] = data.annual_revenue

            if data.burn_rate:
                metrics['burn_rate'] = data.burn_rate

            if data.cash_balance:
                metrics['cash_balance'] = data.cash_balance

            if data.gross_margin:
                metrics['gross_margin'] = data.gross_margin

            # Calculated metrics
            if data.cash_balance and data.burn_rate and data.burn_rate > 0:
                metrics['runway_months'] = data.cash_balance / data.burn_rate

            if data.customer_acquisition_cost and data.lifetime_value and data.customer_acquisition_cost > 0:
                metrics['ltv_cac_ratio'] = data.lifetime_value / data.customer_acquisition_cost

            if data.customers:
                metrics['customer_count'] = data.customers

            if data.employees:
                metrics['employee_count'] = data.employees

            self.log_activity(f"✅ Calculated {len(metrics)} financial metrics from available data")
            return metrics

        except Exception as e:
            self.log_activity(f"❌ Error calculating metrics: {e}")
            return {}

    async def _generate_financial_insights(self, data: ExtractedCompanyData, metrics: Dict[str, Any]) -> List[str]:
        """Generate AI insights based on available financial data"""

        # Create SAFE summary of available data using safe formatting
        available_data_summary = []

        if data.monthly_revenue:
            available_data_summary.append(f"Monthly Revenue: {self.safe_format_currency(data.monthly_revenue)}")
        if data.burn_rate:
            available_data_summary.append(f"Burn Rate: {self.safe_format_currency(data.burn_rate)}/month")
        if data.cash_balance:
            available_data_summary.append(f"Cash Balance: {self.safe_format_currency(data.cash_balance)}")
        if data.customers:
            available_data_summary.append(f"Customers: {self.safe_format_number(data.customers)}")
        if data.employees:
            available_data_summary.append(f"Employees: {self.safe_format_number(data.employees)}")

        prompt = f"""
        Analyze the financial health of this startup:

        Company: {data.company_name or 'Unknown'}
        Sector: {data.sector or 'Unknown'}
        Stage: {data.stage or 'Unknown'}

        AVAILABLE FINANCIAL DATA:
        {'; '.join(available_data_summary) if available_data_summary else 'Very limited financial data available'}

        CALCULATED METRICS:
        {json.dumps(metrics, indent=2) if metrics else 'No metrics could be calculated'}

        Provide 4-6 financial insights covering:
        1. Financial health assessment based on available metrics
        2. Unit economics analysis if data available
        3. Growth trajectory and sustainability
        4. Cash management and runway concerns
        5. Stage-appropriate financial performance

        Format as bullet points. Be specific about investment implications.
        """

        response = await self.call_gemini(prompt)

        if response:
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    insight = line[1:].strip()
                    if len(insight) > 15:
                        insights.append(insight)

            return insights[:6] if insights else self._generate_default_insights(data, metrics)

        return self._generate_default_insights(data, metrics)

    def _generate_default_insights(self, data: ExtractedCompanyData, metrics: Dict[str, Any]) -> List[str]:
        """Generate default insights when AI fails"""
        insights = []

        # SAFE revenue insight using safe formatting
        if data.monthly_revenue and data.monthly_revenue > 0:
            insights.append(f"Company has established revenue stream of {self.safe_format_currency(data.monthly_revenue)}/month")
        else:
            insights.append("No revenue data found - may indicate pre-revenue stage")

        # SAFE burn rate insight
        if data.burn_rate:
            insights.append(f"Monthly burn rate of {self.safe_format_currency(data.burn_rate)} - assess sustainability")
        else:
            insights.append("Burn rate not disclosed - financial sustainability cannot be assessed")

        # SAFE runway insight
        runway = metrics.get('runway_months')
        if runway:
            if runway > 18:
                insights.append(f"Strong financial position with {runway:.1f} months runway")
            elif runway > 12:
                insights.append(f"Adequate runway of {runway:.1f} months")
            else:
                insights.append(f"SHORT RUNWAY WARNING: Only {runway:.1f} months remaining")

        return insights[:6]

    async def _generate_financial_recommendations(self, data: ExtractedCompanyData, metrics: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations"""
        recommendations = []

        runway = metrics.get('runway_months')
        if runway and runway < 12:
            recommendations.append("URGENT: Begin fundraising immediately due to short runway")
        elif runway and runway < 18:
            recommendations.append("Start fundraising process within next quarter")

        ltv_cac = metrics.get('ltv_cac_ratio')
        if ltv_cac and ltv_cac < 3:
            recommendations.append("Focus on improving unit economics")

        if not data.customer_acquisition_cost or not data.lifetime_value:
            recommendations.append("Obtain detailed unit economics data (CAC, LTV)")

        if not recommendations:
            recommendations.append("Continue tracking key financial metrics")

        return recommendations[:4]

    def _detect_financial_flags(self, data: ExtractedCompanyData, metrics: Dict[str, Any]) -> List[str]:
        """Detect financial red flags"""
        flags = []

        runway = metrics.get('runway_months')
        if runway and runway < 6:
            flags.append("CRITICAL: Less than 6 months runway")
        elif runway and runway < 12:
            flags.append("HIGH: Limited runway - funding needed soon")

        ltv_cac = metrics.get('ltv_cac_ratio')
        if ltv_cac and ltv_cac < 1:
            flags.append("CRITICAL: Negative unit economics")

        return flags[:5]

    def _calculate_financial_completeness(self, data: ExtractedCompanyData) -> float:
        """Calculate completeness of financial data"""
        key_fields = [
            data.monthly_revenue, data.burn_rate, data.cash_balance, 
            data.customer_acquisition_cost, data.lifetime_value, 
            data.customers, data.employees, data.gross_margin
        ]

        available_count = sum(1 for field in key_fields if field is not None)
        return available_count / len(key_fields)

    def _calculate_financial_confidence(self, data: ExtractedCompanyData, metrics: Dict[str, Any]) -> float:
        """Calculate confidence in financial analysis"""
        base_confidence = 0.5

        if data.monthly_revenue:
            base_confidence += 0.15
        if data.burn_rate:
            base_confidence += 0.15
        if len(metrics) > 3:
            base_confidence += 0.1

        return min(base_confidence, 0.95)

    def _create_error_response(self, error_msg: str) -> AgentResponse:
        return AgentResponse(
            agent_name=self.agent_name,
            timestamp=datetime.now(),
            confidence_score=0.2,
            findings=[f"Financial analysis failed: {error_msg}"],
            analysis={},
            recommendations=["Provide complete financial data for analysis"],
            flags=[f"CRITICAL: Financial analysis error - {error_msg}"],
            data_completeness=0.0
        )

class EnhancedRiskAssessmentAgent(BaseAgent):
    """Risk Assessment Agent - FIXED VERSION with safe string formatting"""

    def __init__(self, gemini_api_key: str):
        super().__init__("Risk Assessment Agent", gemini_api_key)

    async def assess_risks_from_extracted_data(self, extracted_data: ExtractedCompanyData) -> AgentResponse:
        """Assess risks based on extracted company data - FIXED"""
        self.log_activity(f"Assessing risks for {extracted_data.company_name or 'Unknown Company'}")

        try:
            # Calculate risk scores
            risk_analysis = await self._analyze_risks_with_available_data(extracted_data)

            # Generate risk insights with SAFE formatting
            risk_insights = await self._generate_risk_insights(extracted_data, risk_analysis)

            # Generate mitigation strategies
            recommendations = await self._generate_risk_mitigation_strategies(extracted_data, risk_analysis)

            # Detect critical risk flags
            flags = await self._detect_critical_risk_flags(extracted_data, risk_analysis)

            # Calculate completeness and confidence
            data_completeness = self._calculate_risk_data_completeness(extracted_data)
            confidence = self._calculate_risk_confidence(extracted_data, risk_analysis)

            return AgentResponse(
                agent_name=self.agent_name,
                timestamp=datetime.now(),
                confidence_score=confidence,
                findings=risk_insights,
                analysis=risk_analysis,
                recommendations=recommendations,
                flags=flags,
                data_completeness=data_completeness
            )

        except Exception as e:
            self.log_activity(f"❌ Error in risk assessment: {str(e)}")
            traceback.print_exc()  # Debug info
            return self._create_error_response(str(e))

    async def _analyze_risks_with_available_data(self, data: ExtractedCompanyData) -> Dict[str, Any]:
        """Analyze risks with SAFE handling of None values"""
        risk_analysis = {}

        try:
            # Financial risk
            risk_analysis['financial_risk'] = self._assess_financial_risk(data)

            # Market risk
            risk_analysis['market_risk'] = self._assess_market_risk(data)

            # Team risk
            risk_analysis['team_risk'] = self._assess_team_risk(data)

            # Overall risk score
            risk_scores = [v for v in risk_analysis.values() if isinstance(v, (int, float))]
            risk_analysis['overall_risk_score'] = sum(risk_scores) / len(risk_scores) if risk_scores else 50.0

            return risk_analysis

        except Exception as e:
            self.log_activity(f"❌ Error in risk analysis: {e}")
            return {'error': str(e), 'overall_risk_score': 75.0}

    def _assess_financial_risk(self, data: ExtractedCompanyData) -> float:
        """Assess financial risk - SAFE version"""
        if not data.burn_rate and not data.cash_balance and not data.monthly_revenue:
            return 75.0

        risk_score = 30.0

        # SAFE runway calculation
        if data.burn_rate and data.cash_balance and data.burn_rate > 0:
            runway = data.cash_balance / data.burn_rate
            if runway < 3:
                risk_score += 30.0
            elif runway < 6:
                risk_score += 20.0
            elif runway < 12:
                risk_score += 10.0

        # Revenue risk
        if not data.monthly_revenue:
            if data.stage and data.stage in ['Series A', 'Series B', 'Series C']:
                risk_score += 20.0
            else:
                risk_score += 10.0

        return min(risk_score, 100.0)

    def _assess_market_risk(self, data: ExtractedCompanyData) -> float:
        """Assess market risk - SAFE version"""
        risk_score = 40.0

        if data.sector:
            high_risk_sectors = ['crypto', 'web3', 'gaming']
            if any(s in data.sector.lower() for s in high_risk_sectors):
                risk_score += 20.0
        else:
            risk_score += 15.0

        if data.customers:
            if data.customers < 5:
                risk_score += 25.0
            elif data.customers < 20:
                risk_score += 15.0
        else:
            risk_score += 20.0

        return min(risk_score, 100.0)

    def _assess_team_risk(self, data: ExtractedCompanyData) -> float:
        """Assess team risk - SAFE version"""
        risk_score = 35.0

        if not data.founders and not data.key_team:
            risk_score += 20.0

        if data.employees and data.stage:
            if data.stage in ['Series A', 'Series B'] and data.employees < 10:
                risk_score += 15.0

        return min(risk_score, 100.0)

    async def _generate_risk_insights(self, data: ExtractedCompanyData, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate risk insights with SAFE formatting"""

        # Create SAFE summary using safe formatting methods
        data_summary = f"""
        Company: {data.company_name or 'Unknown'}
        Sector: {data.sector or 'Unknown'}
        Stage: {data.stage or 'Unknown'}
        Revenue: {self.safe_format_currency(data.monthly_revenue)}/month
        Burn Rate: {self.safe_format_currency(data.burn_rate)}/month
        Customers: {self.safe_format_number(data.customers)}
        Employees: {self.safe_format_number(data.employees)}
        """

        prompt = f"""
        Analyze risk profile for this startup:

        {data_summary}

        Risk Scores (0-100, higher = riskier):
        {json.dumps(risk_analysis, indent=2)}

        Provide 5 key risk insights covering:
        1. Primary risk factors for investment
        2. Financial sustainability concerns
        3. Market and competitive risks
        4. Team and execution risks
        5. Stage-appropriate risk assessment

        Format as bullet points with risk level (HIGH/MEDIUM/LOW).
        """

        response = await self.call_gemini(prompt)

        if response:
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    insight = line[1:].strip()
                    if len(insight) > 15:
                        insights.append(insight)

            return insights[:6] if insights else self._generate_default_risk_insights(data, risk_analysis)

        return self._generate_default_risk_insights(data, risk_analysis)

    def _generate_default_risk_insights(self, data: ExtractedCompanyData, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate default risk insights - SAFE version"""
        insights = []

        overall_risk = risk_analysis.get('overall_risk_score', 50.0)

        if overall_risk > 70:
            insights.append("HIGH OVERALL RISK: Multiple risk factors require immediate attention")
        elif overall_risk > 50:
            insights.append("MODERATE RISK: Several areas need monitoring")
        else:
            insights.append("MANAGEABLE RISK: Risk profile within acceptable bounds")

        financial_risk = risk_analysis.get('financial_risk', 50.0)
        if financial_risk > 60:
            insights.append("Financial sustainability risk due to limited runway or missing data")

        market_risk = risk_analysis.get('market_risk', 50.0)
        if market_risk > 60:
            insights.append("Market risk elevated due to sector dynamics or customer concentration")

        return insights[:6]

    async def _generate_risk_mitigation_strategies(self, data: ExtractedCompanyData, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation recommendations"""
        strategies = []

        if risk_analysis.get('financial_risk', 0) > 60:
            strategies.append("Implement strict financial controls and cash flow monitoring")

        if risk_analysis.get('market_risk', 0) > 60:
            strategies.append("Diversify customer base and develop strategic partnerships")

        if not strategies:
            strategies.extend([
                "Establish regular risk monitoring processes",
                "Build advisory board for strategic guidance"
            ])

        return strategies[:4]

    async def _detect_critical_risk_flags(self, data: ExtractedCompanyData, risk_analysis: Dict[str, Any]) -> List[str]:
        """Detect critical risk flags - SAFE version"""
        flags = []

        # SAFE runway flag calculation
        if data.burn_rate and data.cash_balance and data.burn_rate > 0:
            runway = data.cash_balance / data.burn_rate
            if runway < 3:
                flags.append("CRITICAL: Less than 3 months runway")

        if data.stage in ['Series A', 'Series B'] and not data.monthly_revenue:
            flags.append("HIGH: No revenue disclosed at advanced stage")

        overall_risk = risk_analysis.get('overall_risk_score', 50.0)
        if overall_risk > 80:
            flags.append("HIGH: Overall risk above investment threshold")

        return flags[:4]

    def _calculate_risk_data_completeness(self, data: ExtractedCompanyData) -> float:
        """Calculate completeness of risk-relevant data"""
        risk_fields = [
            data.monthly_revenue, data.burn_rate, data.cash_balance,
            data.customers, data.employees, data.founders, data.stage, data.sector
        ]

        available_count = sum(1 for field in risk_fields if field is not None)
        return available_count / len(risk_fields)

    def _calculate_risk_confidence(self, data: ExtractedCompanyData, risk_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in risk assessment"""
        base_confidence = 0.6
        data_completeness = self._calculate_risk_data_completeness(data)
        base_confidence += data_completeness * 0.3
        return min(base_confidence, 0.92)

    def _create_error_response(self, error_msg: str) -> AgentResponse:
        return AgentResponse(
            agent_name=self.agent_name,
            timestamp=datetime.now(),
            confidence_score=0.3,
            findings=[f"Risk assessment failed: {error_msg}"],
            analysis={'error_risk': 100.0},
            recommendations=["Retry risk assessment with complete data"],
            flags=[f"CRITICAL: Risk assessment error - {error_msg}"],
            data_completeness=0.0
        )

class EnhancedMarketIntelligenceAgent(BaseAgent):
    """Market Intelligence Agent - Fixed version"""

    def __init__(self, gemini_api_key: str):
        super().__init__("Market Intelligence Agent", gemini_api_key)

    async def analyze_market_from_extracted_data(self, extracted_data: ExtractedCompanyData) -> AgentResponse:
        """Analyze market opportunity"""
        self.log_activity(f"Analyzing market for {extracted_data.company_name or 'Unknown Company'}")

        try:
            market_insights = await self._generate_market_insights(extracted_data)
            market_analysis = await self._analyze_market_position(extracted_data)
            recommendations = await self._generate_market_recommendations(extracted_data)
            flags = await self._detect_market_flags(extracted_data)

            data_completeness = self._calculate_market_data_completeness(extracted_data)
            confidence = self._calculate_market_confidence(extracted_data, market_insights)

            return AgentResponse(
                agent_name=self.agent_name,
                timestamp=datetime.now(),
                confidence_score=confidence,
                findings=market_insights,
                analysis=market_analysis,
                recommendations=recommendations,
                flags=flags,
                data_completeness=data_completeness
            )

        except Exception as e:
            self.log_activity(f"❌ Error in market analysis: {str(e)}")
            return self._create_error_response(str(e))

    async def _generate_market_insights(self, data: ExtractedCompanyData) -> List[str]:
        """Generate market insights"""

        prompt = f"""
        Analyze market opportunity for this startup:

        Company: {data.company_name or 'Unknown'}
        Sector: {data.sector or 'Unknown'}
        Target Market: {data.target_market or 'Not specified'}
        Product: {data.product_description or 'Not described'}
        Customers: {data.customers or 'Unknown'}
        Stage: {data.stage or 'Unknown'}

        Provide 5 market intelligence insights covering:
        1. Market size and growth potential for this sector
        2. Competitive landscape and positioning
        3. Target customer validation and market fit
        4. Go-to-market strategy effectiveness
        5. Market timing assessment

        Format as bullet points for investment analysis.
        """

        response = await self.call_gemini(prompt)

        if response:
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    insight = line[1:].strip()
                    if len(insight) > 20:
                        insights.append(insight)

            return insights[:6] if insights else self._generate_default_market_insights(data)

        return self._generate_default_market_insights(data)

    def _generate_default_market_insights(self, data: ExtractedCompanyData) -> List[str]:
        """Generate default market insights"""
        insights = []

        if data.sector:
            insights.append(f"Operating in the {data.sector} sector")

        if data.customers:
            if data.customers < 10:
                insights.append("Early customer acquisition phase")
            elif data.customers < 50:
                insights.append("Growing customer base indicates market reception")
            else:
                insights.append("Established customer base suggests product-market fit")

        return insights[:6]

    async def _analyze_market_position(self, data: ExtractedCompanyData) -> Dict[str, Any]:
        """Analyze market position"""
        analysis = {}

        analysis['competitive_advantages_count'] = len(data.competitive_advantages) if data.competitive_advantages else 0

        if data.customers:
            if data.customers < 10:
                analysis['market_maturity'] = 'Early Stage'
            elif data.customers < 100:
                analysis['market_maturity'] = 'Growth Stage'
            else:
                analysis['market_maturity'] = 'Scale Stage'

        return analysis

    async def _generate_market_recommendations(self, data: ExtractedCompanyData) -> List[str]:
        """Generate market recommendations"""
        recommendations = []

        if not data.customers or data.customers < 20:
            recommendations.append("Focus on customer acquisition and market validation")

        if not data.competitive_advantages:
            recommendations.append("Clearly define competitive differentiation")

        if not recommendations:
            recommendations.append("Strengthen market positioning through customer feedback")

        return recommendations[:4]

    async def _detect_market_flags(self, data: ExtractedCompanyData) -> List[str]:
        """Detect market flags"""
        flags = []

        if data.customers and data.customers < 5 and data.stage in ['Series A', 'Series B']:
            flags.append("HIGH: Very small customer base for funding stage")

        if not data.sector or not data.target_market:
            flags.append("MEDIUM: Market definition lacks clarity")

        return flags[:3]

    def _calculate_market_data_completeness(self, data: ExtractedCompanyData) -> float:
        """Calculate market data completeness"""
        market_fields = [
            data.sector, data.target_market, data.product_description,
            data.customers, data.competitive_advantages
        ]

        available_count = sum(1 for field in market_fields if field is not None)
        return available_count / len(market_fields)

    def _calculate_market_confidence(self, data: ExtractedCompanyData, insights: List[str]) -> float:
        """Calculate market confidence"""
        base_confidence = 0.65

        if data.sector and data.target_market:
            base_confidence += 0.1
        if data.customers:
            base_confidence += 0.1
        if len(insights) > 4:
            base_confidence += 0.05

        return min(base_confidence, 0.90)

    def _create_error_response(self, error_msg: str) -> AgentResponse:
        return AgentResponse(
            agent_name=self.agent_name,
            timestamp=datetime.now(),
            confidence_score=0.2,
            findings=[f"Market analysis failed: {error_msg}"],
            analysis={},
            recommendations=["Retry market analysis"],
            flags=[f"HIGH: Market analysis error - {error_msg}"],
            data_completeness=0.0
        )

class BusinessReportGenerationAgent(BaseAgent):
    """COMPLETE Business Report Generation Agent with ALL methods"""

    def __init__(self, gemini_api_key: str):
        super().__init__("Business Report Generation Agent", gemini_api_key)

    async def generate_comprehensive_report(self, 
                                          extracted_data: ExtractedCompanyData, 
                                          agent_responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate comprehensive business report - COMPLETE VERSION"""

        self.log_activity(f"Generating business report for {extracted_data.company_name or 'Unknown Company'}")

        try:
            # Generate all report sections
            executive_summary = await self._generate_executive_summary(extracted_data, agent_responses)
            investment_recommendation = await self._generate_investment_recommendation(extracted_data, agent_responses)

            company_overview = self._generate_company_overview_section(extracted_data)
            financial_analysis_section = self._generate_financial_analysis_section(extracted_data, agent_responses)
            market_analysis_section = self._generate_market_analysis_section(extracted_data, agent_responses)
            risk_analysis_section = self._generate_risk_analysis_section(extracted_data, agent_responses)

            key_metrics = self._extract_key_metrics(extracted_data, agent_responses)
            next_steps = await self._generate_next_steps_and_due_diligence(extracted_data, agent_responses)

            overall_score = self._calculate_overall_investment_score(agent_responses)

            # Compile report
            business_report = {
                "report_metadata": {
                    "company_name": extracted_data.company_name,
                    "analysis_date": datetime.now().isoformat(),
                    "report_type": "Comprehensive Investment Analysis",
                    "analyst_platform": "AI Startup Analyst Platform (Gemini-Powered)",
                    "data_sources": "Document Analysis + AI Intelligence"
                },

                "executive_summary": {
                    "overall_score": overall_score,
                    "investment_recommendation": investment_recommendation,
                    "key_highlights": executive_summary.get("key_highlights", []),
                    "critical_concerns": executive_summary.get("critical_concerns", []),
                    "investment_rationale": executive_summary.get("investment_rationale", "")
                },

                "company_overview": company_overview,

                "detailed_analysis": {
                    "financial_analysis": financial_analysis_section,
                    "market_analysis": market_analysis_section,
                    "risk_analysis": risk_analysis_section
                },

                "key_metrics_summary": key_metrics,
                "next_steps_and_due_diligence": next_steps,

                "appendix": {
                    "data_extraction_summary": self._generate_data_extraction_summary(extracted_data),
                    "agent_confidence_scores": {
                        response.agent_name: response.confidence_score 
                        for response in agent_responses
                    }
                }
            }

            self.log_activity("✅ Comprehensive business report generated")
            return business_report

        except Exception as e:
            self.log_activity(f"❌ Error generating business report: {str(e)}")
            traceback.print_exc()
            return self._generate_error_report(str(e))

    async def _generate_executive_summary(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate executive summary"""

        all_findings = []
        all_flags = []

        for response in responses:
            all_findings.extend(response.findings)
            all_flags.extend(response.flags)

        prompt = f"""
        Create an executive summary for investment analysis:

        Company: {data.company_name or 'Unknown'}
        Sector: {data.sector or 'Unknown'}
        Stage: {data.stage or 'Unknown'}

        KEY FINDINGS:
        {chr(10).join(f"• {finding}" for finding in all_findings[:10])}

        CRITICAL FLAGS:
        {chr(10).join(f"• {flag}" for flag in all_flags[:5])}

        Generate:
        1. KEY HIGHLIGHTS (3-4 strongest positive points)
        2. CRITICAL CONCERNS (2-3 main risk factors)
        3. INVESTMENT RATIONALE (2-3 sentences overall thesis)

        Format as structured sections with bullet points.
        """

        response = await self.call_gemini(prompt)

        if response:
            return self._parse_executive_summary_response(response)

        # Fallback
        return {
            "key_highlights": [
                f"Company operates in {data.sector or 'technology'} sector",
                "AI analysis identifies opportunities for evaluation"
            ],
            "critical_concerns": [
                "Comprehensive due diligence required"
            ],
            "investment_rationale": "Investment opportunity requires further evaluation."
        }

    def _parse_executive_summary_response(self, response: str) -> Dict[str, Any]:
        """Parse executive summary response"""

        sections = {
            "key_highlights": [],
            "critical_concerns": [],
            "investment_rationale": ""
        }

        current_section = None
        current_content = []

        for line in response.split('\n'):
            line = line.strip()

            if 'key highlights' in line.lower() or 'highlights' in line.lower():
                current_section = 'key_highlights'
                continue
            elif 'critical concerns' in line.lower() or 'concerns' in line.lower():
                current_section = 'critical_concerns'
                continue
            elif 'investment rationale' in line.lower() or 'rationale' in line.lower():
                current_section = 'investment_rationale'
                continue

            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                content = line[1:].strip()
                if current_section in ['key_highlights', 'critical_concerns'] and len(content) > 10:
                    sections[current_section].append(content)
            elif current_section == 'investment_rationale' and len(line) > 20:
                current_content.append(line)

        if current_content and current_section == 'investment_rationale':
            sections['investment_rationale'] = ' '.join(current_content)

        return sections

    async def _generate_investment_recommendation(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> str:
        """Generate investment recommendation"""

        all_flags = []
        for response in responses:
            all_flags.extend(response.flags)

        critical_flags = [f for f in all_flags if 'CRITICAL' in f.upper()]
        high_flags = [f for f in all_flags if 'HIGH' in f.upper()]

        avg_confidence = sum(r.confidence_score for r in responses) / len(responses) if responses else 0.5

        prompt = f"""
        Make final investment recommendation for {data.company_name or 'this startup'}:

        Stage: {data.stage or 'Unknown'}
        Sector: {data.sector or 'Unknown'}

        Analysis Results:
        - Average Confidence: {avg_confidence:.1%}
        - Critical Flags: {len(critical_flags)}
        - High Priority Flags: {len(high_flags)}

        Choose ONE recommendation:
        1. "STRONG RECOMMEND" - Exceptional opportunity
        2. "RECOMMEND" - Strong opportunity, manageable risks
        3. "CONSIDER WITH CAUTION" - Mixed signals, needs due diligence
        4. "DO NOT RECOMMEND" - Significant risks
        5. "INSUFFICIENT DATA" - Cannot make recommendation

        Format: "RECOMMENDATION: [2-3 sentence rationale]"
        """

        response = await self.call_gemini(prompt)

        if response:
            return response.strip()

        # Fallback based on flags and confidence
        if critical_flags:
            return "DO NOT RECOMMEND: Critical risk factors pose significant threats to investment success."
        elif len(high_flags) > 3:
            return "CONSIDER WITH CAUTION: Multiple high-priority risks require comprehensive due diligence."
        elif avg_confidence > 0.7:
            return "RECOMMEND: Analysis indicates positive investment opportunity with manageable risks."
        else:
            return "CONSIDER WITH CAUTION: Additional evaluation needed before investment decision."

    def _generate_company_overview_section(self, data: ExtractedCompanyData) -> Dict[str, Any]:
        """Generate company overview section"""

        return {
            "basic_information": {
                "company_name": data.company_name or "Not specified",
                "sector": data.sector or "Not specified",
                "stage": data.stage or "Not specified", 
                "location": data.location or "Not specified",
                "founded_date": data.founded_date or "Not specified",
                "website": data.website or "Not specified"
            },

            "business_description": data.description or "Business description not available",

            "product_and_market": {
                "product_description": data.product_description or "Product details not specified",
                "target_market": data.target_market or "Target market not defined",
                "competitive_advantages": data.competitive_advantages or []
            },

            "team_information": {
                "founders": data.founders or [],
                "key_team": data.key_team or [],
                "total_employees": data.employees
            },

            "funding_information": {
                "current_funding_request": data.funding_request,
                "previous_funding": data.previous_funding
            }
        }

    def _generate_financial_analysis_section(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate financial analysis section"""

        financial_response = next((r for r in responses if 'Financial' in r.agent_name), None)

        return {
            "revenue_metrics": {
                "monthly_revenue": data.monthly_revenue,
                "annual_revenue": data.annual_revenue,
                "growth_rate": data.growth_rate,
                "gross_margin": data.gross_margin
            },

            "cost_and_burn_analysis": {
                "monthly_burn_rate": data.burn_rate,
                "cash_balance": data.cash_balance,
                "runway_months": financial_response.analysis.get('runway_months') if financial_response else None
            },

            "unit_economics": {
                "customer_acquisition_cost": data.customer_acquisition_cost,
                "lifetime_value": data.lifetime_value,
                "ltv_cac_ratio": financial_response.analysis.get('ltv_cac_ratio') if financial_response else None
            },

            "business_metrics": {
                "customer_count": data.customers,
                "employee_count": data.employees,
                "retention_rate": data.retention_rate
            },

            "financial_analysis_summary": financial_response.findings if financial_response else ["Financial analysis not available"],
            "financial_recommendations": financial_response.recommendations if financial_response else [],
            "financial_flags": financial_response.flags if financial_response else []
        }

    def _generate_market_analysis_section(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate market analysis section"""

        market_response = next((r for r in responses if 'Market' in r.agent_name), None)

        return {
            "market_overview": {
                "sector": data.sector,
                "target_market": data.target_market,
                "geographic_focus": data.location
            },

            "competitive_analysis": {
                "competitive_advantages": data.competitive_advantages or [],
                "market_position": market_response.analysis.get('market_maturity') if market_response else 'Unknown'
            },

            "go_to_market_strategy": {
                "current_customers": data.customers
            },

            "market_analysis_insights": market_response.findings if market_response else ["Market analysis not available"],
            "market_recommendations": market_response.recommendations if market_response else [],
            "market_concerns": market_response.flags if market_response else []
        }

    def _generate_risk_analysis_section(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate risk analysis section"""

        risk_response = next((r for r in responses if 'Risk' in r.agent_name), None)

        return {
            "risk_categories": {
                "financial_risk": risk_response.analysis.get('financial_risk') if risk_response else 'Unknown',
                "market_risk": risk_response.analysis.get('market_risk') if risk_response else 'Unknown',
                "team_risk": risk_response.analysis.get('team_risk') if risk_response else 'Unknown',
                "overall_risk_score": risk_response.analysis.get('overall_risk_score') if risk_response else 'Unknown'
            },

            "risk_assessment_summary": risk_response.findings if risk_response else ["Risk analysis not available"],
            "mitigation_strategies": risk_response.recommendations if risk_response else [],
            "critical_risk_flags": risk_response.flags if risk_response else []
        }

    def _extract_key_metrics(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Extract key metrics"""

        metrics = {}

        if data.monthly_revenue:
            metrics['monthly_revenue'] = data.monthly_revenue
            metrics['annual_run_rate'] = data.monthly_revenue * 12

        if data.customers:
            metrics['customer_count'] = data.customers
        if data.employees:
            metrics['employee_count'] = data.employees

        # Add metrics from financial agent
        financial_response = next((r for r in responses if 'Financial' in r.agent_name), None)
        if financial_response:
            metrics.update({
                k: v for k, v in financial_response.analysis.items() 
                if isinstance(v, (int, float))
            })

        return metrics

    async def _generate_next_steps_and_due_diligence(self, data: ExtractedCompanyData, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Generate next steps"""

        return {
            "immediate_next_steps": [
                "Schedule management presentation",
                "Request detailed financial projections", 
                "Conduct customer reference calls",
                "Review legal documentation"
            ],

            "due_diligence_priorities": [
                "Financial model validation",
                "Market validation and competitive analysis",
                "Team background verification",
                "Product demonstration and technical review"
            ],

            "additional_information_requests": [
                "Monthly financial statements",
                "Customer reference contacts",
                "Market research data",
                "Technical documentation"
            ],

            "suggested_timeline": "4-6 weeks for comprehensive due diligence"
        }

    def _calculate_overall_investment_score(self, responses: List[AgentResponse]) -> float:
        """Calculate overall investment score"""

        if not responses:
            return 50.0

        # Agent weights
        agent_weights = {
            'Financial Analysis Agent': 0.30,
            'Risk Assessment Agent': 0.25,
            'Market Intelligence Agent': 0.25,
            'Document Extraction Agent': 0.20
        }

        weighted_score = 0.0
        total_weight = 0.0

        for response in responses:
            weight = agent_weights.get(response.agent_name, 0.15)

            # Base score from confidence
            base_score = response.confidence_score * 100

            # Adjust for flags
            critical_flags = len([f for f in response.flags if 'CRITICAL' in f.upper()])
            high_flags = len([f for f in response.flags if 'HIGH' in f.upper()])

            penalty = (critical_flags * 25) + (high_flags * 10)
            agent_score = max(base_score - penalty, 0)

            weighted_score += agent_score * weight
            total_weight += weight

        final_score = weighted_score / total_weight if total_weight > 0 else 50.0
        return round(min(max(final_score, 0), 100), 1)

    def _generate_data_extraction_summary(self, data: ExtractedCompanyData) -> Dict[str, Any]:
        """Generate data extraction summary"""

        extracted_fields = []
        missing_fields = []

        for field_name, field_value in asdict(data).items():
            if field_name == 'extraction_confidence':
                continue
            if field_value is not None:
                extracted_fields.append(field_name)
            else:
                missing_fields.append(field_name)

        return {
            "total_data_points": len(extracted_fields) + len(missing_fields),
            "successfully_extracted": len(extracted_fields),
            "missing_data_points": len(missing_fields),
            "extraction_rate": len(extracted_fields) / (len(extracted_fields) + len(missing_fields)),
            "extraction_confidence": data.extraction_confidence or {}
        }

    def _generate_error_report(self, error_msg: str) -> Dict[str, Any]:
        """Generate error report"""
        return {
            "report_metadata": {
                "report_type": "Error Report",
                "analysis_date": datetime.now().isoformat(),
                "error": error_msg
            },
            "executive_summary": {
                "overall_score": 0.0,
                "investment_recommendation": f"REPORT GENERATION FAILED: {error_msg}",
                "key_highlights": [],
                "critical_concerns": [f"System error: {error_msg}"],
                "investment_rationale": "Cannot provide recommendation due to system error."
            },
            "error_details": {
                "error_message": error_msg,
                "recommended_action": "Retry analysis with system debugging"
            }
        }

class DocumentDrivenOrchestrator:
    """Main Orchestrator - COMPLETE FIXED VERSION"""

    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key

        if not GEMINI_AVAILABLE:
            raise Exception("Google Generative AI not available. Install: pip install google-generativeai")

        if not gemini_api_key:
            raise Exception("Gemini API key is required")

        # Initialize all agents
        try:
            self.extraction_agent = DocumentExtractionAgent(gemini_api_key)
            self.financial_agent = EnhancedFinancialAnalysisAgent(gemini_api_key)
            self.risk_agent = EnhancedRiskAssessmentAgent(gemini_api_key)
            self.market_agent = EnhancedMarketIntelligenceAgent(gemini_api_key)
            self.report_agent = BusinessReportGenerationAgent(gemini_api_key)

            logger.info("✅ All document-driven AI agents initialized successfully (Gemini API only)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {str(e)}")
            raise

    async def analyze_startup_from_documents(self, request: DocumentAnalysisRequest) -> Dict[str, Any]:
        """Complete analysis pipeline - FIXED VERSION"""
        logger.info("🚀 Starting document-driven AI analysis (Gemini API only)")
        start_time = datetime.now()

        try:
            # STEP 1: Extract data
            logger.info("📄 STEP 1: Extracting company data from documents...")
            extracted_data = await self.extraction_agent.extract_company_data(request)

            if not extracted_data.company_name:
                extracted_data.company_name = request.company_name or "Unknown Company"

            logger.info(f"✅ Data extracted for {extracted_data.company_name}")

            # STEP 2: Run analysis agents
            logger.info("🤖 STEP 2: Running AI analysis agents...")

            agent_responses = []

            # Financial Analysis
            logger.info("💰 Running Financial Analysis Agent...")
            financial_response = await self.financial_agent.analyze_extracted_data(extracted_data)
            agent_responses.append(financial_response)

            # Risk Assessment  
            logger.info("⚠️ Running Risk Assessment Agent...")
            risk_response = await self.risk_agent.assess_risks_from_extracted_data(extracted_data)
            agent_responses.append(risk_response)

            # Market Intelligence
            logger.info("📈 Running Market Intelligence Agent...")
            market_response = await self.market_agent.analyze_market_from_extracted_data(extracted_data)
            agent_responses.append(market_response)

            # STEP 3: Generate report
            logger.info("📋 STEP 3: Generating comprehensive business report...")
            business_report = await self.report_agent.generate_comprehensive_report(extracted_data, agent_responses)

            # Add metadata
            duration = (datetime.now() - start_time).total_seconds()
            business_report["analysis_metadata"] = {
                "analysis_duration_seconds": round(duration, 1),
                "agents_processed": len(agent_responses) + 1,
                "documents_processed": len(request.documents),
                "analysis_type": "Document-Driven AI Analysis (Gemini API Only)"
            }

            logger.info(f"✅ Analysis completed in {duration:.1f} seconds")
            return business_report

        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            traceback.print_exc()

            return {
                "analysis_metadata": {
                    "analysis_duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "system_error": str(e)
                },
                "executive_summary": {
                    "overall_score": 0.0,
                    "investment_recommendation": f"ANALYSIS FAILED - {str(e)}",
                    "key_highlights": [],
                    "critical_concerns": [f"System error: {str(e)}"],
                    "investment_rationale": "Cannot provide recommendation due to system error."
                }
            }

    def get_system_health(self) -> Dict[str, str]:
        """Check system health"""
        health_status = {
            "status": "healthy",
            "agents_status": {},
            "google_services": {}
        }

        agents = [
            ("document_extraction", self.extraction_agent),
            ("financial_analysis", self.financial_agent), 
            ("risk_assessment", self.risk_agent),
            ("market_intelligence", self.market_agent),
            ("business_report_generation", self.report_agent)
        ]

        for agent_name, agent in agents:
            if agent and hasattr(agent, 'gemini_model') and agent.gemini_model:
                health_status["agents_status"][agent_name] = "ready"
            else:
                health_status["agents_status"][agent_name] = "error"

        try:
            if self.gemini_api_key:
                health_status["google_services"]["gemini_api"] = "connected"
                health_status["google_services"]["cloud_vision"] = "not_required"
            else:
                health_status["google_services"]["gemini_api"] = "no_api_key"
        except Exception as e:
            health_status["google_services"]["error"] = str(e)

        return health_status

# Setup function for external imports
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_environment():
    """Validate environment setup"""
    if not GEMINI_AVAILABLE:
        raise Exception("Google Generative AI not available. Run: pip install google-generativeai")

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise Exception("GEMINI_API_KEY environment variable not set")

    return api_key
