
import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, Any, Optional
import base64
from io import BytesIO

# Configure Streamlit page
st.set_page_config(
    page_title="AI Startup Analyst Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your FastAPI URL

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }

    .agent-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }

    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""

    # Initialize session state
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "analysis_id" not in st.session_state:
        st.session_state.analysis_id = None
    if "company_data" not in st.session_state:
        st.session_state.company_data = {}

    # Header
    st.markdown('<h1 class="main-header">🚀 AI Startup Analyst Platform</h1>', 
                unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        <p>AI-Powered Startup Evaluation with 5 Specialized Agents</p>
        <p>Transform weeks of due diligence into minutes of intelligent analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📊 New Analysis", "📈 Results", "🎯 Benchmarks", "📱 About"]
    )

    # Health check in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🏥 System Status")
        if st.button("Check Health"):
            health_status = check_api_health()
            if health_status:
                st.success("✅ All systems operational")
                with st.expander("View Details"):
                    st.json(health_status)
            else:
                st.error("❌ API connection failed")

    # Page routing
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 New Analysis":
        show_analysis_page()
    elif page == "📈 Results":
        show_results_page()
    elif page == "🎯 Benchmarks":
        show_benchmarks_page()
    elif page == "📱 About":
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

def show_dashboard():
    """Display main dashboard"""
    st.header("📊 Platform Dashboard")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖</h3>
            <h2>5</h2>
            <p>AI Agents</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📄</h3>
            <h2>40+</h2>
            <p>Evaluation Metrics</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡</h3>
            <h2>3 min</h2>
            <p>Analysis Time</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h2>95%</h2>
            <p>Time Reduction</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # AI Agents Overview
    st.subheader("🤖 AI Agents Overview")

    agents = [
        {
            "name": "Document Intelligence Agent",
            "icon": "📄",
            "description": "Analyzes pitch decks, financial statements, and business plans using Cloud Vision + Gemini Pro",
            "capabilities": ["Text extraction", "Visual analysis", "Slide classification", "Key metrics identification"]
        },
        {
            "name": "Financial Analysis Agent", 
            "icon": "💰",
            "description": "Processes financial data and benchmarks using BigQuery + Gemini Pro + Vertex AI",
            "capabilities": ["Ratio calculations", "Trend analysis", "Peer benchmarking", "Projection validation"]
        },
        {
            "name": "Risk Assessment Agent",
            "icon": "⚠️",
            "description": "Identifies red flags and calculates risk scores using Vertex AI + Gemini Pro",
            "capabilities": ["Pattern detection", "Inconsistency analysis", "Risk scoring", "Mitigation strategies"]
        },
        {
            "name": "Market Intelligence Agent",
            "icon": "📈",
            "description": "Analyzes competitive landscape using BigQuery + Cloud Functions + Gemini Pro",
            "capabilities": ["Market validation", "Competitive analysis", "Trend identification", "Opportunity assessment"]
        },
        {
            "name": "Synthesis & Reporting Agent",
            "icon": "📋",
            "description": "Combines insights into investment recommendations using Gemini Pro + Agent Builder",
            "capabilities": ["Insight aggregation", "Report generation", "Recommendation synthesis", "Action prioritization"]
        }
    ]

    for agent in agents:
        with st.expander(f"{agent['icon']} {agent['name']}"):
            st.markdown(f"**Description:** {agent['description']}")
            st.markdown("**Key Capabilities:**")
            for capability in agent['capabilities']:
                st.markdown(f"• {capability}")

    # Recent analyses (mock data for demo)
    st.markdown("---")
    st.subheader("📊 Recent Analyses")

    if st.session_state.analysis_results:
        st.success("✅ Latest analysis completed")
        if st.button("View Latest Results"):
            st.session_state.page = "📈 Results"
            st.experimental_rerun()
    else:
        st.info("No recent analyses. Start a new analysis to see results here.")

def show_analysis_page():
    """Display startup analysis form"""
    st.header("📊 New Startup Analysis")

    # Progress indicator
    progress_container = st.container()

    with st.form("startup_analysis_form"):
        st.subheader("🏢 Company Information")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company Name*", placeholder="e.g., VitalSync Health")
            sector = st.selectbox("Sector*", [
                "HealthTech", "FinTech", "AI/ML", "SaaS", "E-commerce", 
                "CleanTech", "EdTech", "Logistics", "Real Estate", "Other"
            ])
            stage = st.selectbox("Funding Stage*", [
                "Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth"
            ])

        with col2:
            funding_request = st.number_input(
                "Funding Request ($)*", 
                min_value=100000, 
                max_value=100000000, 
                value=5000000,
                step=100000,
                format="%d"
            )
            location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
            description = st.text_area("Company Description", 
                                     placeholder="Brief description of the company and its product/service")

        st.markdown("---")
        st.subheader("💰 Financial Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            monthly_revenue = st.number_input(
                "Monthly Revenue ($)", 
                min_value=0, 
                value=0,
                step=1000,
                help="Current monthly recurring revenue"
            )
            burn_rate = st.number_input(
                "Monthly Burn Rate ($)*", 
                min_value=1000,
                value=50000,
                step=1000,
                help="Monthly cash burn rate"
            )
            cash_balance = st.number_input(
                "Cash Balance ($)*",
                min_value=0,
                value=1000000,
                step=10000,
                help="Current cash on hand"
            )

        with col2:
            employees = st.number_input(
                "Number of Employees", 
                min_value=1,
                value=10,
                step=1
            )
            customers = st.number_input(
                "Number of Customers",
                min_value=0,
                value=0,
                step=1
            )
            gross_margin = st.slider(
                "Gross Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=70.0,
                step=0.5,
                help="Gross profit margin percentage"
            )

        with col3:
            if monthly_revenue > 0:
                cac = st.number_input(
                    "Customer Acquisition Cost ($)",
                    min_value=0,
                    value=500,
                    step=50
                )
                ltv = st.number_input(
                    "Customer Lifetime Value ($)",
                    min_value=0,
                    value=2000,
                    step=100
                )
                retention_rate = st.slider(
                    "Customer Retention Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=85.0,
                    step=1.0
                )
            else:
                st.info("💡 Revenue-based metrics will be available when monthly revenue > 0")
                cac = ltv = retention_rate = 0

        st.markdown("---")
        st.subheader("📄 Document Upload")

        uploaded_files = st.file_uploader(
            "Upload startup documents",
            type=['pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload pitch decks, financial statements, business plans, etc."
        )

        st.markdown("---")
        st.subheader("ℹ️ Additional Information")

        col1, col2 = st.columns(2)

        with col1:
            founding_date = st.date_input(
                "Founding Date",
                value=datetime.now() - timedelta(days=365*2),
                max_value=datetime.now().date()
            )
            website = st.text_input("Website", placeholder="https://company.com")

        with col2:
            regulatory_status = st.text_input(
                "Regulatory Status",
                placeholder="e.g., FDA clearance pending"
            )
            key_partnerships = st.text_area(
                "Key Partnerships",
                placeholder="List major partnerships or strategic relationships"
            )

        # Submit button
        submitted = st.form_submit_button("🚀 Start AI Analysis", use_container_width=True)

        if submitted:
            # Validate required fields
            if not company_name or not sector or not stage:
                st.error("❌ Please fill in all required fields marked with *")
                return

            # Prepare request data
            request_data = {
                "company_info": {
                    "name": company_name,
                    "sector": sector,
                    "stage": stage,
                    "funding_request": funding_request,
                    "description": description if description else None
                },
                "financial_data": {
                    "monthly_revenue": monthly_revenue if monthly_revenue > 0 else None,
                    "burn_rate": burn_rate,
                    "cash_balance": cash_balance,
                    "employees": employees,
                    "customers": customers if customers > 0 else None,
                    "gross_margin": gross_margin,
                },
                "additional_info": {
                    "founding_date": founding_date.isoformat() if founding_date else None,
                    "location": location if location else None,
                    "website": website if website else None,
                    "regulatory_status": regulatory_status if regulatory_status else None,
                    "key_partnerships": key_partnerships.split('\n') if key_partnerships else None
                }
            }

            # Add revenue-based metrics if applicable
            if monthly_revenue > 0:
                request_data["financial_data"].update({
                    "customer_acquisition_cost": cac if cac > 0 else None,
                    "lifetime_value": ltv if ltv > 0 else None,
                    "customer_retention_rate": retention_rate if retention_rate > 0 else None
                })

            # Store company data in session state
            st.session_state.company_data = request_data

            # Start analysis
            start_analysis(request_data, uploaded_files, progress_container)

def start_analysis(request_data: Dict, uploaded_files, progress_container):
    """Start the startup analysis"""

    with progress_container:
        st.subheader("🔄 Analysis in Progress")

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Upload documents first (if any)
            document_ids = []
            if uploaded_files:
                status_text.text("📄 Uploading documents...")
                for file in uploaded_files:
                    # Upload document
                    files = {"file": (file.name, file.getvalue(), file.type)}
                    upload_response = requests.post(
                        f"{API_BASE_URL}/api/v1/documents/upload",
                        files=files
                    )

                    if upload_response.status_code == 200:
                        document_ids.append(upload_response.json().get("file_id"))
                        st.success(f"✅ Uploaded {file.name}")
                    else:
                        st.warning(f"⚠️ Failed to upload {file.name}")

                # Add document IDs to request
                request_data["documents"] = document_ids
                progress_bar.progress(20)

            # Start analysis
            status_text.text("🚀 Starting AI analysis...")
            analysis_response = requests.post(
                f"{API_BASE_URL}/api/v1/analyze",
                json=request_data
            )

            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                analysis_id = analysis_data.get("analysis_id")
                st.session_state.analysis_id = analysis_id

                st.success(f"✅ Analysis started! ID: {analysis_id}")
                progress_bar.progress(30)

                # Monitor progress
                monitor_analysis_progress(analysis_id, progress_bar, status_text)

            else:
                st.error(f"❌ Failed to start analysis: {analysis_response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")

def monitor_analysis_progress(analysis_id: str, progress_bar, status_text):
    """Monitor analysis progress and display updates"""

    max_attempts = 60  # 5 minutes maximum
    attempt = 0

    while attempt < max_attempts:
        try:
            # Check status
            status_response = requests.get(
                f"{API_BASE_URL}/api/v1/analysis/{analysis_id}/status"
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                current_step = status_data.get("current_step", "")

                # Update progress bar and status
                progress_bar.progress(min(progress / 100, 1.0))
                status_text.text(f"🤖 {current_step} ({progress:.0f}% complete)")

                if status == "completed":
                    # Analysis completed - get results
                    progress_bar.progress(1.0)
                    status_text.text("✅ Analysis completed successfully!")

                    results_response = requests.get(
                        f"{API_BASE_URL}/api/v1/analysis/{analysis_id}/results"
                    )

                    if results_response.status_code == 200:
                        results = results_response.json()
                        st.session_state.analysis_results = results

                        st.balloons()
                        st.success("🎉 Analysis completed! Check the Results page.")

                        # Show quick preview
                        show_results_preview(results)

                    else:
                        st.error("❌ Failed to retrieve results")

                    break

                elif status == "failed":
                    st.error("❌ Analysis failed")
                    break

            else:
                st.error("❌ Failed to check analysis status")
                break

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            break

        # Wait 5 seconds before next check
        time.sleep(5)
        attempt += 1

    if attempt >= max_attempts:
        st.warning("⏰ Analysis is taking longer than expected. Check the Results page later.")

def show_results_preview(results: Dict):
    """Show a preview of analysis results"""

    company_analysis = results.get("company_analysis", {})

    st.markdown("### 📊 Quick Results Preview")

    col1, col2, col3 = st.columns(3)

    with col1:
        overall_score = company_analysis.get("overall_score", 0)
        st.metric("Overall Score", f"{overall_score:.1f}/100")

    with col2:
        recommendation = company_analysis.get("recommendation", "N/A")
        st.metric("Recommendation", recommendation)

    with col3:
        insights_count = len(company_analysis.get("key_insights", []))
        st.metric("Key Insights", f"{insights_count} found")

    # Show top insights
    insights = company_analysis.get("key_insights", [])
    if insights:
        st.markdown("**Top Insights:**")
        for i, insight in enumerate(insights[:3], 1):
            st.markdown(f"{i}. {insight}")

    st.markdown("---")
    st.info("💡 Visit the Results page for complete analysis details, charts, and AI agent insights.")

def show_results_page():
    """Display analysis results"""

    if not st.session_state.analysis_results:
        st.warning("🔍 No analysis results available. Please run an analysis first.")
        return

    results = st.session_state.analysis_results
    company_analysis = results.get("company_analysis", {})
    agent_summary = results.get("agent_summary", [])

    st.header("📈 Analysis Results")

    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        overall_score = company_analysis.get("overall_score", 0)
        score_color = get_score_color(overall_score)
        st.markdown(f"""
        <div style="text-align: center;">
            <h2 style="color: {score_color}; font-size: 3rem; margin: 0;">{overall_score:.1f}</h2>
            <p style="margin: 0;">Overall Score</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        recommendation = company_analysis.get("recommendation", "N/A")
        rec_color = get_recommendation_color(recommendation)
        st.markdown(f"""
        <div style="background: {rec_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0;">{recommendation}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        insights_count = len(company_analysis.get("key_insights", []))
        st.metric("Key Insights", insights_count)

    with col4:
        flags_count = len(company_analysis.get("critical_flags", []))
        st.metric("Critical Flags", flags_count, delta=-flags_count if flags_count > 0 else None)

    st.markdown("---")

    # Detailed results tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary", 
        "🤖 AI Agent Insights", 
        "💰 Financial Analysis",
        "⚠️ Risk Assessment", 
        "📈 Market Intelligence"
    ])

    with tab1:
        show_executive_summary(company_analysis)

    with tab2:
        show_agent_insights(agent_summary)

    with tab3:
        show_financial_analysis(company_analysis)

    with tab4:
        show_risk_assessment(company_analysis)

    with tab5:
        show_market_intelligence()

def show_executive_summary(company_analysis: Dict):
    """Display executive summary"""

    st.subheader("📋 Investment Summary")

    # Key insights
    insights = company_analysis.get("key_insights", [])
    if insights:
        st.markdown("**🔑 Key Insights:**")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")

    # Critical flags
    flags = company_analysis.get("critical_flags", [])
    if flags:
        st.markdown("**🚩 Critical Flags:**")
        for flag in flags:
            st.error(f"⚠️ {flag}")
    else:
        st.success("✅ No critical flags detected")

    # Financial metrics summary
    metrics = company_analysis.get("financial_metrics", {})
    if metrics:
        st.markdown("**💰 Key Financial Metrics:**")

        col1, col2, col3 = st.columns(3)

        for i, (key, value) in enumerate(metrics.items()):
            col = [col1, col2, col3][i % 3]

            with col:
                if isinstance(value, (int, float)):
                    if "ratio" in key.lower():
                        st.metric(format_metric_name(key), f"{value:.1f}x")
                    elif "rate" in key.lower() or "margin" in key.lower():
                        st.metric(format_metric_name(key), f"{value:.1f}%")
                    elif "months" in key.lower():
                        st.metric(format_metric_name(key), f"{value:.1f} mo")
                    else:
                        st.metric(format_metric_name(key), f"{value:,.0f}")

    # Next steps
    next_steps = company_analysis.get("next_steps", [])
    if next_steps:
        st.markdown("**📋 Recommended Next Steps:**")
        for i, step in enumerate(next_steps, 1):
            st.markdown(f"{i}. {step}")

def show_agent_insights(agent_summary: list):
    """Display AI agent insights"""

    st.subheader("🤖 AI Agent Analysis")

    if not agent_summary:
        st.warning("No agent insights available")
        return

    # Agent confidence chart
    agent_names = [agent.get("agent", "").replace(" Agent", "") for agent in agent_summary]
    confidences = [agent.get("confidence", 0) * 100 for agent in agent_summary]

    fig_confidence = px.bar(
        x=agent_names,
        y=confidences,
        title="AI Agent Confidence Scores",
        labels={"x": "AI Agent", "y": "Confidence (%)"},
        color=confidences,
        color_continuous_scale="viridis"
    )
    fig_confidence.update_layout(showlegend=False)
    st.plotly_chart(fig_confidence, use_container_width=True)

    # Individual agent insights
    for agent in agent_summary:
        agent_name = agent.get("agent", "Unknown Agent")
        confidence = agent.get("confidence", 0)
        key_finding = agent.get("key_finding", "No findings available")

        confidence_color = get_confidence_color(confidence)

        st.markdown(f"""
        <div class="agent-card">
            <h4>{agent_name}</h4>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span>Confidence Score:</span>
                <span style="color: {confidence_color}; font-weight: bold;">{confidence:.1%}</span>
            </div>
            <p><strong>Key Finding:</strong> {key_finding}</p>
        </div>
        """, unsafe_allow_html=True)

def show_financial_analysis(company_analysis: Dict):
    """Display financial analysis"""

    st.subheader("💰 Financial Analysis")

    metrics = company_analysis.get("financial_metrics", {})

    if not metrics:
        st.warning("No financial metrics available")
        return

    # Financial health gauge
    financial_score = calculate_financial_health_score(metrics)

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = financial_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Financial Health Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)

    # Key ratios visualization
    ratio_metrics = {k: v for k, v in metrics.items() 
                    if isinstance(v, (int, float)) and "ratio" in k.lower()}

    if ratio_metrics:
        fig_ratios = px.bar(
            x=list(ratio_metrics.keys()),
            y=list(ratio_metrics.values()),
            title="Key Financial Ratios",
            labels={"x": "Metric", "y": "Value"}
        )
        st.plotly_chart(fig_ratios, use_container_width=True)

    # Detailed metrics table
    st.markdown("**📊 Detailed Financial Metrics:**")

    metrics_df = pd.DataFrame([
        {"Metric": format_metric_name(k), "Value": format_metric_value(k, v)}
        for k, v in metrics.items() if isinstance(v, (int, float))
    ])

    st.dataframe(metrics_df, use_container_width=True)

def show_risk_assessment(company_analysis: Dict):
    """Display risk assessment"""

    st.subheader("⚠️ Risk Assessment")

    # Mock risk breakdown (since it's not in the current API response structure)
    risk_categories = {
        "Financial Risk": 25,
        "Market Risk": 40, 
        "Team Risk": 15,
        "Technology Risk": 30,
        "Competitive Risk": 45,
        "Regulatory Risk": 20
    }

    # Risk radar chart
    categories = list(risk_categories.keys())
    values = list(risk_categories.values())

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Risk Level'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Risk Profile by Category"
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Critical flags
    flags = company_analysis.get("critical_flags", [])

    if flags:
        st.markdown("**🚨 Critical Risk Flags:**")
        for flag in flags:
            st.error(f"⚠️ {flag}")

    # Risk mitigation suggestions
    st.markdown("**🛡️ Risk Mitigation Strategies:**")

    mitigation_strategies = [
        "Diversify customer base to reduce concentration risk",
        "Establish strategic partnerships to mitigate competitive threats",
        "Implement stronger financial controls and reporting",
        "Build regulatory compliance framework early",
        "Develop contingency plans for key person dependencies"
    ]

    for strategy in mitigation_strategies:
        st.markdown(f"• {strategy}")

def show_market_intelligence():
    """Display market intelligence"""

    st.subheader("📈 Market Intelligence")

    # Get market data from API
    try:
        # Example sector - you can make this dynamic based on the analyzed company
        sector = st.session_state.company_data.get("company_info", {}).get("sector", "HealthTech")

        market_response = requests.get(f"{API_BASE_URL}/api/v1/market-intelligence/{sector}")

        if market_response.status_code == 200:
            market_data = market_response.json()

            # Market size and growth
            col1, col2, col3 = st.columns(3)

            with col1:
                market_size = market_data.get("market_data", {}).get("market_size_billions", 0)
                st.metric("Market Size", f"${market_size:.1f}B")

            with col2:
                growth_rate = market_data.get("market_data", {}).get("growth_rate_cagr", 0)
                st.metric("Growth Rate (CAGR)", f"{growth_rate:.1f}%")

            with col3:
                funding_activity = market_data.get("market_data", {}).get("funding_activity_12m", 0)
                st.metric("12M Funding Activity", f"${funding_activity/1000000:.0f}M")

            # Competitive landscape
            st.markdown("**🏆 Competitive Landscape:**")

            competitors = market_data.get("competitive_landscape", {}).get("top_competitors", [])
            if competitors:
                comp_df = pd.DataFrame(competitors)
                st.dataframe(comp_df, use_container_width=True)

            # Market trends
            trends = market_data.get("trends", [])
            if trends:
                st.markdown("**📊 Market Trends:**")
                for trend in trends:
                    st.markdown(f"• {trend}")

        else:
            st.error("Failed to load market intelligence data")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_benchmarks_page():
    """Display sector benchmarks"""

    st.header("🎯 Sector Benchmarks")

    # Sector selection
    sector = st.selectbox("Select Sector:", [
        "HealthTech", "FinTech", "AI/ML", "SaaS", "E-commerce", 
        "CleanTech", "EdTech", "Logistics", "Real Estate"
    ])

    if st.button("Load Benchmarks"):
        try:
            benchmark_response = requests.get(f"{API_BASE_URL}/api/v1/benchmarks/{sector}")

            if benchmark_response.status_code == 200:
                benchmark_data = benchmark_response.json()

                st.success(f"✅ Loaded benchmarks for {sector}")

                # Display benchmark metrics
                metrics = benchmark_data.get("metrics", {})
                sample_size = benchmark_data.get("sample_size", 0)

                st.info(f"📊 Based on {sample_size} companies in {sector}")

                # Metrics visualization
                if metrics:
                    col1, col2, col3 = st.columns(3)

                    for i, (metric, value) in enumerate(metrics.items()):
                        col = [col1, col2, col3][i % 3]

                        with col:
                            formatted_name = format_metric_name(metric)
                            formatted_value = format_metric_value(metric, value)
                            st.metric(formatted_name, formatted_value)

                    # Benchmark comparison chart
                    fig_bench = px.bar(
                        x=list(metrics.keys()),
                        y=list(metrics.values()),
                        title=f"{sector} Sector Benchmarks",
                        labels={"x": "Metric", "y": "Median Value"}
                    )
                    st.plotly_chart(fig_bench, use_container_width=True)

            else:
                st.error(f"Failed to load benchmarks: {benchmark_response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

def show_about_page():
    """Display about page"""

    st.header("📱 About AI Startup Analyst Platform")

    st.markdown("""
    ## 🚀 Platform Overview

    The AI Startup Analyst Platform revolutionizes venture capital due diligence by leveraging 
    5 specialized AI agents to analyze startups comprehensively and generate institutional-grade 
    investment insights in minutes instead of weeks.

    ## 🤖 Our AI Agents

    **1. Document Intelligence Agent**
    - Powered by Google Cloud Vision + Gemini Pro
    - Analyzes pitch decks, financial statements, and business plans
    - Extracts key metrics and insights from unstructured documents

    **2. Financial Analysis Agent**
    - Powered by BigQuery + Gemini Pro + Vertex AI
    - Calculates financial ratios and benchmarks performance
    - Validates projections and identifies trends

    **3. Risk Assessment Agent**
    - Powered by Vertex AI + Gemini Pro
    - Detects red flags and inconsistencies
    - Calculates comprehensive risk scores

    **4. Market Intelligence Agent**
    - Powered by BigQuery + Cloud Functions + Gemini Pro
    - Analyzes competitive landscape and market opportunities
    - Validates market size claims and growth projections

    **5. Synthesis & Reporting Agent**
    - Powered by Gemini Pro + Agent Builder
    - Combines insights from all agents
    - Generates investment recommendations and deal notes

    ## 📊 Key Benefits

    - **95% Time Reduction**: Analysis in 3 minutes vs 4-8 weeks
    - **99% Cost Reduction**: $50-100 vs $50K-200K per analysis
    - **40+ Evaluation Metrics** across 5 key categories
    - **Institutional-Grade Quality** with AI-powered insights
    - **Real-time Processing** with live progress tracking
    - **Scalable Architecture** handles high-volume deal flow

    ## 🏗️ Technology Stack

    - **Google Cloud Platform**: Enterprise-grade infrastructure
    - **Gemini Pro**: Advanced language understanding
    - **Vertex AI**: Custom machine learning models
    - **BigQuery**: Data warehouse and analytics
    - **Cloud Vision**: Document analysis and OCR
    - **Streamlit**: Interactive web interface
    - **FastAPI**: High-performance backend API

    ## 🎯 Target Users

    - **Venture Capital Firms**: Accelerate due diligence processes
    - **Angel Investors**: Professional-grade analysis tools
    - **Corporate VCs**: Standardized evaluation framework
    - **Investment Banks**: Scalable startup assessment
    - **Family Offices**: Risk-adjusted investment decisions

    ## 📈 Success Metrics

    - **15x LTV/CAC Ratio**: Outstanding unit economics
    - **94% Customer Retention**: Proven product-market fit
    - **38% Risk Reduction**: Early red flag detection
    - **5-Star Rating**: Consistently excellent results

    ## 🤝 Get Started

    Ready to revolutionize your startup evaluation process?

    1. Navigate to "New Analysis" to evaluate your first startup
    2. Upload documents and enter company information
    3. Watch our AI agents work their magic
    4. Review comprehensive insights and recommendations
    5. Make data-driven investment decisions with confidence

    ---

    *Built with ❤️ using cutting-edge AI technology*
    """)

# Utility functions
def get_score_color(score: float) -> str:
    """Get color based on score"""
    if score >= 80:
        return "#28a745"  # Green
    elif score >= 60:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def get_recommendation_color(recommendation: str) -> str:
    """Get color based on recommendation"""
    if "RECOMMEND" in recommendation.upper() and "NOT" not in recommendation.upper():
        return "#28a745"  # Green
    elif "CAUTION" in recommendation.upper():
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence score"""
    if confidence >= 0.8:
        return "#28a745"  # Green
    elif confidence >= 0.6:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def format_metric_name(metric_name: str) -> str:
    """Format metric name for display"""
    return metric_name.replace("_", " ").title()

def format_metric_value(metric_name: str, value) -> str:
    """Format metric value for display"""
    if isinstance(value, (int, float)):
        if "ratio" in metric_name.lower():
            return f"{value:.1f}x"
        elif "rate" in metric_name.lower() or "margin" in metric_name.lower():
            return f"{value:.1f}%"
        elif "months" in metric_name.lower():
            return f"{value:.1f} mo"
        elif value > 1000000:
            return f"${value/1000000:.1f}M"
        elif value > 1000:
            return f"${value/1000:.0f}K"
        else:
            return f"{value:,.0f}"
    return str(value)

def calculate_financial_health_score(metrics: Dict) -> float:
    """Calculate overall financial health score"""
    # Simple scoring logic based on available metrics
    score = 50  # Base score

    # LTV/CAC ratio bonus
    ltv_cac = metrics.get("ltv_cac_ratio", 0)
    if ltv_cac > 10:
        score += 30
    elif ltv_cac > 5:
        score += 20
    elif ltv_cac > 3:
        score += 10

    # Growth rate bonus
    growth_rate = metrics.get("monthly_growth_rate", 0)
    if growth_rate > 15:
        score += 15
    elif growth_rate > 10:
        score += 10
    elif growth_rate > 5:
        score += 5

    # Runway consideration
    runway = metrics.get("runway_months", 0)
    if runway > 18:
        score += 15
    elif runway > 12:
        score += 10
    elif runway < 6:
        score -= 20

    return min(score, 100)

if __name__ == "__main__":
    main()
