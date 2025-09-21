
# VITALSYNC HEALTH API TESTING COMMANDS
# Complete set of curl commands to test the AI Startup Analyst Platform

# 1. HEALTH CHECK
echo "🏥 Testing Health Check..."
curl -X GET "http://localhost:8000/health" \
     -H "accept: application/json"

echo "\n\n"

# 2. UPLOAD DOCUMENTS (if testing document upload)
echo "📄 Uploading Pitch Deck..."
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_data/vitalsync_pitch_deck.txt"

echo "\n\n"

echo "📊 Uploading Financial Statements..."
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_data/vitalsync_financial_statements.txt"

echo "\n\n"

# 3. START COMPREHENSIVE ANALYSIS
echo "🤖 Starting Comprehensive Startup Analysis..."
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -H "accept: application/json" \
     -d '{
       "company_info": {
         "name": "VitalSync Health",
         "sector": "HealthTech",
         "stage": "Series A",
         "funding_request": 8000000,
         "description": "AI-Powered Remote Patient Monitoring Platform"
       },
       "financial_data": {
         "monthly_revenue": 180000,
         "annual_run_rate": 2160000,
         "burn_rate": 220000,
         "cash_balance": 3800000,
         "employees": 28,
         "customers": 45,
         "gross_margin": 82.5,
         "customer_acquisition_cost": 1200,
         "lifetime_value": 18000,
         "monthly_growth_rate": 12.5,
         "customer_retention_rate": 94,
         "net_revenue_retention": 115,
         "runway_months": 17.3
       },
       "documents": [
         "test_data/vitalsync_pitch_deck.txt",
         "test_data/vitalsync_financial_statements.txt"
       ],
       "additional_info": {
         "founding_date": "2022-03-15",
         "location": "Austin, Texas",
         "regulatory_status": "FDA 510(k) clearance obtained",
         "clinical_outcomes": {
           "readmission_reduction": 38,
           "cost_savings_per_patient": 3200,
           "patient_satisfaction": 4.7
         }
       }
     }'

# Note: Copy the analysis_id from the response above

echo "\n\n"

# 4. CHECK ANALYSIS STATUS (replace ANALYSIS_ID with actual ID)
echo "📊 Checking Analysis Status..."
ANALYSIS_ID="your-analysis-id-here"
curl -X GET "http://localhost:8000/api/v1/analysis/$ANALYSIS_ID/status" \
     -H "accept: application/json"

echo "\n\n"

# 5. GET ANALYSIS RESULTS (once completed)
echo "📋 Getting Analysis Results..."
curl -X GET "http://localhost:8000/api/v1/analysis/$ANALYSIS_ID/results" \
     -H "accept: application/json" | jq '.'

echo "\n\n"

# 6. GET SECTOR BENCHMARKS
echo "🎯 Getting HealthTech Sector Benchmarks..."
curl -X GET "http://localhost:8000/api/v1/benchmarks/HealthTech" \
     -H "accept: application/json"

echo "\n\n"

# 7. GET MARKET INTELLIGENCE  
echo "📈 Getting Market Intelligence..."
curl -X GET "http://localhost:8000/api/v1/market-intelligence/HealthTech" \
     -H "accept: application/json"

echo "\n\n"

# 8. TEST RED FLAGS SCENARIO
echo "🚩 Testing Red Flags Detection..."
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -H "accept: application/json" \
     -d '{
       "company_info": {
         "name": "VitalSync Health (Red Flags Test)",
         "sector": "HealthTech",
         "stage": "Series A",
         "funding_request": 15000000
       },
       "financial_data": {
         "monthly_revenue": 50000,
         "burn_rate": 350000,
         "cash_balance": 800000,
         "employees": 45,
         "customers": 8,
         "customer_retention_rate": 75,
         "runway_months": 2.3
       },
       "additional_info": {
         "customer_concentration": 85,
         "notes": "High-risk scenario to test red flag detection"
       }
     }'

echo "\n\n"

# 9. BASIC HEALTH METRICS TEST
echo "💊 Testing with Basic Health Metrics..."
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -H "accept: application/json" \
     -d '{
       "company_info": {
         "name": "VitalSync Health Basic",
         "sector": "HealthTech",
         "stage": "Seed",
         "funding_request": 2000000
       },
       "financial_data": {
         "monthly_revenue": 25000,
         "burn_rate": 85000,
         "cash_balance": 500000,
         "employees": 8,
         "customers": 12
       }
     }'

echo "\nAPI Testing Complete! 🎉"
