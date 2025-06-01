from langchain_community.utilities import SQLDatabase
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load API keys
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("❌ OPENAI_API_KEY not set!")
print(f"✅ OpenAI Key Loaded: {openai_key[:8]}...")

POSTGRES_URL = os.getenv("POSTGRES")
if not POSTGRES_URL:
    raise ValueError("❌ POSTGRES environment variable not set!")
print(f"🔗 Connecting to DB: {POSTGRES_URL}")

# 1. Connect to PostgreSQL
db = SQLDatabase.from_uri(POSTGRES_URL)

# 2. Initialize Chat Model
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# 3. Prompt Template
prompt = PromptTemplate.from_template("""
Given the following customer data:

{customer_data}

Suggest a personalized cross-sell offer. Include:
- Recommended Product/Service
- Why this is a good fit
- Estimated success probability

Only suggest relevant, ethical, and valuable offers.
""")

# 4. Chain prompt → LLM using | pipe operator (RunnableSequence replacement)
chain = prompt | llm

# 5. Query Customer Info
customer_id = 'GC000001'
customer_query = f"""
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.age,
  c.annual_income,
  f.credit_score,
  f.risk_profile,
  d.app_logins_last_month,
  d.last_login,
  s.average_balance,
  pl.status AS personal_loan_status,
  hl.status AS home_loan_status,
  hl.loan_amount,
  i.type AS insurance_type,
  i.status AS insurance_status
FROM customers c
LEFT JOIN financial_behavior f ON c.customer_id = f.customer_id
LEFT JOIN digital_engagement d ON c.customer_id = d.customer_id
LEFT JOIN savings_accounts s ON c.customer_id = s.customer_id
LEFT JOIN personal_loans pl ON c.customer_id = pl.customer_id
LEFT JOIN home_loans hl ON c.customer_id = hl.customer_id
LEFT JOIN insurances i ON c.customer_id = i.customer_id
WHERE c.customer_id = '{customer_id}';
"""

# 6. Fetch Data
try:
    customer_data = db.run(customer_query)
except Exception as e:
    raise RuntimeError(f"❌ Failed to fetch customer data: {e}")

# 7. Generate Recommendation
result = chain.invoke({"customer_data": customer_data})
print("🎯 Personalized Offer:\n", result.content)
