
import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Document-Driven AI Startup Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for business report styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }

    .business-report {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }

    .executive-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .score-display {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    .recommendation-strong {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }

    .recommendation-caution {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }

    .recommendation-negative {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }

    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #eee;
    }

    .upload-zone {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background: #f8f9fa;
    }

    .progress-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""

    # Initialize session state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "analysis_id" not in st.session_state:
        st.session_state.analysis_id = None
    if "business_report" not in st.session_state:
        st.session_state.business_report = None

    # Header
    st.markdown('<h1 class="main-header">📊 Document-Driven AI Startup Analyst</h1>', 
                unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        <h3>Upload Documents → Get Professional Investment Analysis</h3>
        <p>Upload pitch decks, financial statements, or business plans. Our AI extracts all information and generates a comprehensive business report with investment recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("📁 Document Analysis")
    page = st.sidebar.radio(
        "Choose action:",
        ["📤 Upload & Analyze", "📊 View Report", "ℹ️ About"]
    )

    # System status in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🏥 System Status")
        if st.button("Check Status", key="health_check"):
            health_status = check_api_health()
            if health_status and health_status.get("status") == "healthy":
                st.success("✅ AI system operational")
            else:
                st.error("❌ AI system unavailable")

    # Page routing
    if page == "📤 Upload & Analyze":
        show_upload_and_analyze_page()
    elif page == "📊 View Report":
        show_report_page()
    elif page == "ℹ️ About":
        show_about_page()

def check_api_health() -> Optional[Dict]:
    """Check API health status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def show_upload_and_analyze_page():
    """Show document upload and analysis page"""

    st.header("📤 Upload Documents for Analysis")

    # Instructions
    st.markdown("""
    **📋 Instructions:**
    1. Upload your startup documents (pitch deck, financial statements, business plan, etc.)
    2. Optionally add any additional context or information
    3. Click "Start AI Analysis" to get a professional business report

    **Supported formats:** PDF, PowerPoint (.pptx), Word (.docx), Text files
    """)

    # File upload section
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "📁 Upload Startup Documents",
        type=['pdf', 'pptx', 'docx', 'txt', 'md'],
        accept_multiple_files=True,
        help="Upload pitch decks, financial statements, business plans, or any relevant documents"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} document(s) uploaded successfully!")

        # Display uploaded files
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            st.markdown(f"📄 **{file.name}** ({file_size_mb:.1f} MB)")

    # Optional information section
    st.markdown("---")
    st.subheader("💬 Additional Information (Optional)")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            "Company Name (Optional)", 
            placeholder="e.g., VitalSync Health",
            help="Helps AI focus the analysis if not clear from documents"
        )

    with col2:
        pass  # Empty column for spacing

    additional_writeup = st.text_area(
        "Additional Context",
        placeholder="Any additional information not in the documents (market insights, recent developments, specific questions, etc.)",
        height=150,
        help="Provide any context that might help with the analysis"
    )

    # Analysis button
    st.markdown("---")

    if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("❌ Please upload at least one document before starting analysis")
            return

        # Upload files and start analysis
        start_document_analysis(uploaded_files, company_name, additional_writeup)

def start_document_analysis(uploaded_files: List, company_name: str, additional_writeup: str):
    """Upload files and start document analysis"""

    with st.spinner("📤 Uploading documents..."):
        # Upload files to backend
        uploaded_file_paths = []

        for file in uploaded_files:
            try:
                files = {"file": (file.name, file.getvalue(), file.type)}
                response = requests.post(f"{API_BASE_URL}/api/v1/documents/upload", files=files)

                if response.status_code == 200:
                    file_data = response.json()
                    uploaded_file_paths.append(file_data["file_path"])
                    st.success(f"✅ Uploaded {file.name}")
                else:
                    st.error(f"❌ Failed to upload {file.name}")
                    return

            except Exception as e:
                st.error(f"❌ Upload error for {file.name}: {str(e)}")
                return

    # Start analysis
    try:
        analysis_data = {
            "company_name": company_name if company_name else None,
            "document_paths": json.dumps(uploaded_file_paths),
            "additional_writeup": additional_writeup if additional_writeup else None
        }

        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze-documents",
            data=analysis_data
        )

        if response.status_code == 200:
            result = response.json()
            st.session_state.analysis_id = result["analysis_id"]

            st.success("✅ Analysis started successfully!")
            st.info(f"Analysis ID: {result['analysis_id']}")

            # Show progress
            monitor_analysis_progress(result["analysis_id"])

        else:
            st.error(f"❌ Failed to start analysis: {response.text}")

    except Exception as e:
        st.error(f"❌ Analysis error: {str(e)}")

def monitor_analysis_progress(analysis_id: str):
    """Monitor and display analysis progress"""

    progress_container = st.empty()
    status_container = st.empty()

    max_attempts = 60  # 5 minutes maximum
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE_URL}/api/v1/analysis/{analysis_id}/status")

            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                current_step = status_data.get("current_step", "")

                # Update progress display
                with progress_container.container():
                    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                    st.markdown("### 🔄 Analysis in Progress")
                    st.progress(progress / 100)
                    st.markdown(f"**Current Step:** {current_step}")
                    st.markdown(f"**Progress:** {progress:.0f}%")
                    st.markdown('</div>', unsafe_allow_html=True)

                if status == "completed":
                    progress_container.empty()
                    status_container.success("🎉 Analysis completed successfully!")

                    # Load and display results
                    load_business_report(analysis_id)
                    break

                elif status == "failed":
                    progress_container.empty()
                    error = status_data.get("error", "Unknown error")
                    status_container.error(f"❌ Analysis failed: {error}")
                    break

            else:
                st.error("❌ Failed to check analysis status")
                break

        except Exception as e:
            st.error(f"❌ Status check error: {str(e)}")
            break

        time.sleep(5)
        attempt += 1

    if attempt >= max_attempts:
        progress_container.empty()
        st.warning("⏰ Analysis is taking longer than expected. Check the View Report page later.")

def load_business_report(analysis_id: str):
    """Load and store business report"""

    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/analysis/{analysis_id}/report")

        if response.status_code == 200:
            st.session_state.business_report = response.json()
            st.success("📊 Business report generated successfully!")
            st.info("📈 Click 'View Report' in the sidebar to see the full analysis.")

            # Show quick preview
            show_report_preview(st.session_state.business_report)

        else:
            st.error("❌ Failed to load business report")

    except Exception as e:
        st.error(f"❌ Report loading error: {str(e)}")

def show_report_preview(report: Dict[str, Any]):
    """Show a quick preview of the business report"""

    if not report:
        return

    executive_summary = report.get("executive_summary", {})

    st.markdown("### 📊 Quick Report Preview")

    col1, col2, col3 = st.columns(3)

    with col1:
        score = executive_summary.get("overall_score", 0)
        st.metric("Overall Score", f"{score}/100")

    with col2:
        recommendation = executive_summary.get("investment_recommendation", "N/A")
        if "RECOMMEND" in recommendation.upper() and "NOT" not in recommendation.upper():
            st.success("✅ Positive Recommendation")
        elif "CAUTION" in recommendation.upper():
            st.warning("⚠️ Proceed with Caution")
        else:
            st.error("❌ Negative Recommendation")

    with col3:
        company_name = report.get("report_metadata", {}).get("company_name", "Unknown")
        st.info(f"Company: {company_name}")

def show_report_page():
    """Display the comprehensive business report"""

    if not st.session_state.business_report:
        st.warning("📊 No business report available. Please upload documents and run analysis first.")
        return

    report = st.session_state.business_report

    # Report header
    metadata = report.get("report_metadata", {})
    company_name = metadata.get("company_name", "Unknown Company")
    analysis_date = metadata.get("analysis_date", "")

    st.markdown(f'<h1 class="main-header">📊 Investment Analysis Report</h1>', 
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        <h2>{company_name}</h2>
        <p>Analysis Date: {analysis_date[:10] if analysis_date else 'Unknown'}</p>
        <p>Generated by AI Startup Analyst Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Executive Summary
    show_executive_summary_section(report)

    # Detailed Analysis Tabs
    st.markdown("---")
    st.markdown('<h2 class="section-header">📋 Detailed Analysis</h2>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Company Overview",
        "💰 Financial Analysis", 
        "📈 Market Analysis",
        "⚠️ Risk Analysis",
        "📊 Key Metrics"
    ])

    with tab1:
        show_company_overview_section(report)

    with tab2:
        show_financial_analysis_section(report)

    with tab3:
        show_market_analysis_section(report)

    with tab4:
        show_risk_analysis_section(report)

    with tab5:
        show_key_metrics_section(report)

    # Next Steps
    show_next_steps_section(report)

def show_executive_summary_section(report: Dict[str, Any]):
    """Display executive summary section"""

    executive_summary = report.get("executive_summary", {})

    st.markdown('<div class="executive-summary">', unsafe_allow_html=True)
    st.markdown("## 📋 Executive Summary")

    # Overall Score and Recommendation
    col1, col2 = st.columns(2)

    with col1:
        score = executive_summary.get("overall_score", 0)
        st.markdown(f"""
        <div class="score-display">
            <h1 style="margin: 0; color: #1f77b4;">{score}/100</h1>
            <p style="margin: 0;">Overall Investment Score</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        recommendation = executive_summary.get("investment_recommendation", "")

        # Style recommendation based on content
        if "STRONG RECOMMEND" in recommendation.upper():
            rec_class = "recommendation-strong"
        elif "RECOMMEND" in recommendation.upper() and "NOT" not in recommendation.upper():
            rec_class = "recommendation-strong"
        elif "CAUTION" in recommendation.upper():
            rec_class = "recommendation-caution"
        else:
            rec_class = "recommendation-negative"

        st.markdown(f"""
        <div class="{rec_class}">
            <h3 style="margin-top: 0;">Investment Recommendation</h3>
            <p style="margin-bottom: 0;">{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Key Highlights and Concerns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Key Highlights")
        highlights = executive_summary.get("key_highlights", [])
        for highlight in highlights:
            st.markdown(f"• {highlight}")

    with col2:
        st.markdown("### ⚠️ Critical Concerns")
        concerns = executive_summary.get("critical_concerns", [])
        for concern in concerns:
            st.markdown(f"• {concern}")

    # Investment Rationale
    rationale = executive_summary.get("investment_rationale", "")
    if rationale:
        st.markdown("### 🎯 Investment Rationale")
        st.markdown(rationale)

def show_company_overview_section(report: Dict[str, Any]):
    """Display company overview section"""

    company_overview = report.get("company_overview", {})

    # Basic Information
    st.markdown("### 🏢 Basic Information")
    basic_info = company_overview.get("basic_information", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Company Name:** {basic_info.get('company_name', 'N/A')}")
        st.markdown(f"**Sector:** {basic_info.get('sector', 'N/A')}")
        st.markdown(f"**Stage:** {basic_info.get('stage', 'N/A')}")

    with col2:
        st.markdown(f"**Location:** {basic_info.get('location', 'N/A')}")
        st.markdown(f"**Founded:** {basic_info.get('founded_date', 'N/A')}")
        st.markdown(f"**Website:** {basic_info.get('website', 'N/A')}")

    # Business Description
    business_desc = company_overview.get("business_description", "")
    if business_desc and business_desc != "Business description not available from documents":
        st.markdown("### 📖 Business Description")
        st.markdown(business_desc)

    # Product and Market
    product_market = company_overview.get("product_and_market", {})

    st.markdown("### 📦 Product & Market")

    product_desc = product_market.get("product_description", "")
    if product_desc and product_desc != "Product details not specified":
        st.markdown(f"**Product:** {product_desc}")

    target_market = product_market.get("target_market", "")
    if target_market and target_market != "Target market not clearly defined":
        st.markdown(f"**Target Market:** {target_market}")

    advantages = product_market.get("competitive_advantages", [])
    if advantages:
        st.markdown("**Competitive Advantages:**")
        for advantage in advantages:
            st.markdown(f"• {advantage}")

    # Team Information
    team_info = company_overview.get("team_information", {})

    col1, col2 = st.columns(2)

    with col1:
        founders = team_info.get("founders", [])
        if founders:
            st.markdown("**Founders:**")
            for founder in founders:
                st.markdown(f"• {founder}")

    with col2:
        employees = team_info.get("total_employees")
        if employees:
            st.markdown(f"**Team Size:** {employees} employees")

def show_financial_analysis_section(report: Dict[str, Any]):
    """Display financial analysis section"""

    financial_section = report.get("detailed_analysis", {}).get("financial_analysis", {})

    # Revenue Metrics
    st.markdown("### 💰 Revenue Metrics")
    revenue_metrics = financial_section.get("revenue_metrics", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        monthly_rev = revenue_metrics.get("monthly_revenue")
        if monthly_rev:
            st.metric("Monthly Revenue", f"${monthly_rev:,.0f}")

    with col2:
        annual_rev = revenue_metrics.get("annual_revenue")
        if annual_rev:
            st.metric("Annual Revenue", f"${annual_rev:,.0f}")

    with col3:
        growth_rate = revenue_metrics.get("growth_rate")
        if growth_rate:
            st.metric("Growth Rate", f"{growth_rate:.1f}%/month")

    # Cash and Burn Analysis
    st.markdown("### 🔥 Cash & Burn Analysis")
    burn_analysis = financial_section.get("cost_and_burn_analysis", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        burn_rate = burn_analysis.get("monthly_burn_rate")
        if burn_rate:
            st.metric("Monthly Burn", f"${burn_rate:,.0f}")

    with col2:
        cash_balance = burn_analysis.get("cash_balance")
        if cash_balance:
            st.metric("Cash Balance", f"${cash_balance:,.0f}")

    with col3:
        runway = burn_analysis.get("runway_months")
        if runway:
            st.metric("Runway", f"{runway:.1f} months")

    # Unit Economics
    unit_economics = financial_section.get("unit_economics", {})
    ltv_cac_ratio = unit_economics.get("ltv_cac_ratio")

    if ltv_cac_ratio:
        st.markdown("### 📊 Unit Economics")

        col1, col2, col3 = st.columns(3)

        with col1:
            cac = unit_economics.get("customer_acquisition_cost")
            if cac:
                st.metric("CAC", f"${cac:,.0f}")

        with col2:
            ltv = unit_economics.get("lifetime_value")
            if ltv:
                st.metric("LTV", f"${ltv:,.0f}")

        with col3:
            st.metric("LTV/CAC Ratio", f"{ltv_cac_ratio:.1f}x")

    # Financial Insights
    insights = financial_section.get("financial_analysis_summary", [])
    if insights and insights != ["Financial analysis not available"]:
        st.markdown("### 💡 Financial Insights")
        for insight in insights:
            st.markdown(f"• {insight}")

def show_market_analysis_section(report: Dict[str, Any]):
    """Display market analysis section"""

    market_section = report.get("detailed_analysis", {}).get("market_analysis", {})

    # Market Overview
    st.markdown("### 📈 Market Overview")
    market_overview = market_section.get("market_overview", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Sector:** {market_overview.get('sector', 'N/A')}")
        st.markdown(f"**Geographic Focus:** {market_overview.get('geographic_focus', 'N/A')}")

    with col2:
        target_market = market_overview.get("target_market", "")
        if target_market and target_market != "Not specified":
            st.markdown(f"**Target Market:** {target_market}")

    # Go-to-Market Strategy
    gtm = market_section.get("go_to_market_strategy", {})

    st.markdown("### 🎯 Go-to-Market")

    col1, col2 = st.columns(2)

    with col1:
        customers = gtm.get("current_customers")
        if customers:
            st.metric("Current Customers", f"{customers:,}")

    with col2:
        penetration = gtm.get("market_penetration")
        if penetration:
            st.metric("Market Penetration", f"{penetration:.2f}%")

    # Partnerships
    partnerships = gtm.get("partnerships", [])
    if partnerships:
        st.markdown("**Strategic Partnerships:**")
        for partnership in partnerships:
            st.markdown(f"• {partnership}")

    # Market Insights
    insights = market_section.get("market_analysis_insights", [])
    if insights and insights != ["Market analysis not available"]:
        st.markdown("### 💡 Market Insights")
        for insight in insights:
            st.markdown(f"• {insight}")

def show_risk_analysis_section(report: Dict[str, Any]):
    """Display risk analysis section"""

    risk_section = report.get("detailed_analysis", {}).get("risk_analysis", {})

    # Risk Categories
    st.markdown("### ⚠️ Risk Assessment")
    risk_categories = risk_section.get("risk_categories", {})

    if risk_categories:
        col1, col2 = st.columns(2)

        with col1:
            financial_risk = risk_categories.get("financial_risk")
            if financial_risk and financial_risk != 'Unknown':
                st.metric("Financial Risk", f"{financial_risk:.0f}/100")

            market_risk = risk_categories.get("market_risk")
            if market_risk and market_risk != 'Unknown':
                st.metric("Market Risk", f"{market_risk:.0f}/100")

        with col2:
            team_risk = risk_categories.get("team_risk")
            if team_risk and team_risk != 'Unknown':
                st.metric("Team Risk", f"{team_risk:.0f}/100")

            overall_risk = risk_categories.get("overall_risk_score")
            if overall_risk and overall_risk != 'Unknown':
                st.metric("Overall Risk", f"{overall_risk:.0f}/100")

    # Risk Insights
    risk_insights = risk_section.get("risk_assessment_summary", [])
    if risk_insights and risk_insights != ["Risk analysis not available"]:
        st.markdown("### 🔍 Risk Analysis")
        for insight in risk_insights:
            st.markdown(f"• {insight}")

    # Critical Flags
    flags = risk_section.get("critical_risk_flags", [])
    if flags:
        st.markdown("### 🚩 Critical Risk Flags")
        for flag in flags:
            if "CRITICAL" in flag.upper():
                st.error(f"🚨 {flag}")
            elif "HIGH" in flag.upper():
                st.warning(f"⚠️ {flag}")
            else:
                st.info(f"ℹ️ {flag}")

def show_key_metrics_section(report: Dict[str, Any]):
    """Display key metrics summary"""

    key_metrics = report.get("key_metrics_summary", {})

    if not key_metrics:
        st.warning("No key metrics available")
        return

    st.markdown("### 📊 Key Metrics Summary")

    # Create metrics display
    metrics_to_display = []

    for metric, value in key_metrics.items():
        if isinstance(value, (int, float)) and value is not None:
            formatted_name = metric.replace('_', ' ').title()

            if 'revenue' in metric.lower() or 'balance' in metric.lower():
                formatted_value = f"${value:,.0f}"
            elif 'ratio' in metric.lower():
                formatted_value = f"{value:.1f}x"
            elif 'rate' in metric.lower() or 'margin' in metric.lower():
                formatted_value = f"{value:.1f}%"
            elif 'months' in metric.lower():
                formatted_value = f"{value:.1f} mo"
            else:
                formatted_value = f"{value:,.0f}"

            metrics_to_display.append((formatted_name, formatted_value))

    # Display metrics in columns
    if metrics_to_display:
        num_cols = min(3, len(metrics_to_display))
        cols = st.columns(num_cols)

        for i, (name, value) in enumerate(metrics_to_display):
            col_idx = i % num_cols
            with cols[col_idx]:
                st.metric(name, value)

def show_next_steps_section(report: Dict[str, Any]):
    """Display next steps and due diligence section"""

    next_steps_section = report.get("next_steps_and_due_diligence", {})

    if not next_steps_section:
        return

    st.markdown("---")
    st.markdown('<h2 class="section-header">📝 Next Steps & Due Diligence</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Immediate Next Steps
        immediate_steps = next_steps_section.get("immediate_next_steps", [])
        if immediate_steps:
            st.markdown("### 🚀 Immediate Next Steps")
            for i, step in enumerate(immediate_steps, 1):
                st.markdown(f"{i}. {step}")

        # Timeline
        timeline = next_steps_section.get("suggested_timeline", "")
        if timeline:
            st.markdown("### ⏰ Suggested Timeline")
            st.info(timeline)

    with col2:
        # Due Diligence Priorities
        dd_priorities = next_steps_section.get("due_diligence_priorities", [])
        if dd_priorities:
            st.markdown("### 🔍 Due Diligence Priorities")
            for priority in dd_priorities:
                st.markdown(f"• {priority}")

        # Information Requests
        info_requests = next_steps_section.get("additional_information_requests", [])
        if info_requests:
            st.markdown("### 📋 Information Requests")
            for request in info_requests:
                st.markdown(f"• {request}")

def show_about_page():
    """Display about page"""

    st.header("ℹ️ About Document-Driven AI Startup Analyst")

    st.markdown("""
    ## 🚀 How It Works

    This AI-powered platform revolutionizes startup analysis by extracting ALL information directly from your documents:

    ### 📤 **Step 1: Upload Documents**
    - Upload pitch decks, financial statements, business plans
    - Supports PDF, PowerPoint, Word documents
    - No manual data entry required!

    ### 🤖 **Step 2: AI Document Extraction**
    - **Document Extraction Agent** reads and understands all your documents
    - Automatically extracts company info, financials, team data, market info
    - Uses Google Gemini Pro for intelligent document comprehension

    ### 📊 **Step 3: Multi-Agent Analysis**
    - **Financial Analysis Agent**: Calculates metrics, analyzes health
    - **Risk Assessment Agent**: Identifies risks and red flags  
    - **Market Intelligence Agent**: Evaluates opportunity and competition
    - **Business Report Agent**: Synthesizes insights into professional report

    ### 📋 **Step 4: Professional Business Report**
    - Executive summary with investment recommendation
    - Detailed financial, market, and risk analysis
    - Next steps and due diligence recommendations
    - Professional format suitable for investment committees

    ## 🎯 **Key Benefits**

    ✅ **No Manual Data Entry** - Just upload documents  
    ✅ **Comprehensive Analysis** - 5 AI agents working together  
    ✅ **Professional Reports** - Investment-grade business analysis  
    ✅ **Fast Processing** - 2-3 minutes vs weeks of manual work  
    ✅ **Real AI Intelligence** - Powered by Google Gemini Pro  
    ✅ **Document-Driven** - Extracts insights from actual materials  

    ## 💡 **Best Practices**

    - **Upload multiple documents** for more comprehensive analysis
    - **Include pitch decks** for company overview and strategy
    - **Add financial statements** for detailed metrics
    - **Provide business plans** for market and operational insights  
    - **Use recent documents** for accurate analysis

    ## 🔧 **Supported Document Types**

    | Format | Description | Recommended |
    |--------|-------------|-------------|
    | **PDF** | Portable Document Format | ✅ Best |
    | **PPTX** | PowerPoint Presentations | ✅ Best |  
    | **DOCX** | Word Documents | ✅ Good |
    | **TXT** | Plain Text Files | ⚠️ Limited |

    ## 🚀 **Ready to Get Started?**

    Click "Upload & Analyze" to upload your startup documents and get a professional AI-powered investment analysis report!

    ---

    *Powered by Google Gemini Pro AI and advanced document intelligence*
    """)

if __name__ == "__main__":
    main()
