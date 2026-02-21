# AI Resume Analyzer
It is an AI Resume Analyzer bulid with React , tailwind front end and fastapi , rag and langchain, langgraph used in backend
to run the app in your local browser use following commands. 

# Navigate to backend
cd backend
# Create a virtual environment
python -m venv venv
# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Create your .env file
echo GROQ_API_KEY=your_groq_api_key_here > .env
# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Navigate to frontend
cd frontend
# Install Node modules
npm install
# Start the development server
npm run dev
