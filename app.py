from langchain_community.utilities import SQLDatabase
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# 1. Connect to PostgreSQL
db = SQLDatabase.from_uri(os.getenv("POSTGRES"))

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

def get_customer_query(customer_id: str = "GC000001") -> str:
    """
    Generate SQL query to fetch customer data based on customer_id.
    Default customer_id is 'GC000001'.
    """
    return f"""
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

app = FastAPI()

# Mount static files and templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_user(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/customer/{customer_id}")
def get_customer_offer(customer_id: str):
    """
    Fetch personalized offer for a given customer ID.
    """
    try:
        # Fetch customer data
        customer_data = db.run(get_customer_query(customer_id))
        
        # Generate recommendation
        result = chain.invoke({"customer_data": customer_data})
        
        return {"personalized_offer": result.content}
    
    except Exception as e:
        return {"error": str(e)}


