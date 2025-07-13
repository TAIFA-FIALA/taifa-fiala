#!/bin/bash

# TAIFA-FIALA Rwanda Demo Startup Script
# This script starts all necessary services for the demo

echo "🇷🇼 TAIFA-FIALA Rwanda Demo Setup"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "demo_rwanda_pipeline.py" ]; then
    echo "❌ Please run this script from the ai-africa-funding-tracker directory"
    exit 1
fi

# Check environment variables
echo "🔧 Checking environment variables..."

if [ -z "$SERPER_DEV_API_KEY" ]; then
    echo "⚠️  SERPER_DEV_API_KEY not found in environment"
    echo "   Please add your SERPER API key to .env file"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not found in environment" 
    echo "   Please check your database configuration in .env"
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "✅ Loading environment variables from .env"
    export $(cat .env | grep -v ^# | xargs)
else
    echo "⚠️  .env file not found. Using system environment variables."
fi

echo ""
echo "🚀 Demo Options:"
echo "1. 🎬 Run Rwanda Demo (Simulated Daily Collection)"
echo "2. 🖥️  Start Next.js Frontend (Professional UI)"
echo "3. 📊 Start Streamlit Backend Admin"
echo "4. ⚙️  Start FastAPI Backend Only"
echo "5. 🌐 Start Backend + Next.js Frontend"
echo "6. 🕐 Start Daily Collection Scheduler (Production)"
echo "7. 🧪 Test API Connection"

read -p "Choose option (1-7): " choice

case $choice in
    1)
        echo ""
        echo "🎬 Running Rwanda Demo (Simulated Daily Collection)..."
        echo "This demonstrates:"
        echo "  - Scheduled daily collection process (simulated)"
        echo "  - Database storage and processing"
        echo "  - User search experience (instant local search)"
        echo "  - Complete architecture showcase"
        echo ""
        python demo_rwanda_pipeline.py
        ;;
    2)
        echo ""
        echo "🖥️  Starting Next.js Frontend (Professional UI)..."
        echo "   📍 URL: http://localhost:3000"
        echo "   🔗 Rwanda Demo: /rwanda-demo"
        echo "   ⚡ Professional bilingual interface"
        echo ""
        cd frontend/nextjs_dashboard
        npm run dev
        ;;
    3)
        echo ""
        echo "📊 Starting Streamlit Backend Admin..."
        echo "   📍 URL: http://localhost:8501"
        echo "   🔧 Backend administration interface"
        echo "   📈 Data management and monitoring"
        echo ""
        cd frontend/streamlit_app
        streamlit run app.py
        ;;
    4)
        echo ""
        echo "⚙️  Starting FastAPI Backend..."
        echo "   📍 URL: http://localhost:8000"
        echo "   📚 API Docs: http://localhost:8000/docs"
        echo ""
        cd backend
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    5)
        echo ""
        echo "🌐 Starting Backend + Next.js Frontend (DEMO MODE)..."
        echo "   📍 Backend: http://localhost:8000"
        echo "   📍 Frontend: http://localhost:3000"
        echo "   🇷🇼 Rwanda Demo: http://localhost:3000/rwanda-demo"
        echo ""
        
        # Start backend in background
        echo "Starting FastAPI backend..."
        cd backend
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ..
        
        # Wait for backend to start
        echo "Waiting for backend to start..."
        sleep 5
        
        # Start Next.js frontend
        echo "Starting Next.js frontend..."
        cd frontend/nextjs_dashboard
        npm run dev &
        FRONTEND_PID=$!
        cd ../..
        
        echo ""
        echo "✅ Demo environment ready!"
        echo "   🔧 Backend PID: $BACKEND_PID"
        echo "   🖥️  Frontend PID: $FRONTEND_PID"
        echo "   🇷🇼 Rwanda Demo: http://localhost:3000/rwanda-demo"
        echo ""
        echo "Press Ctrl+C to stop both services"
        
        # Wait for user interrupt
        trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
        wait
        ;;
    6)
        echo ""
        echo "🕐 Starting Daily Collection Scheduler..."
        echo "This runs the production scheduler that:"
        echo "  - Collects funding opportunities daily at 6 AM"
        echo "  - Cleans up expired opportunities weekly"
        echo "  - Sends notifications on completion"
        echo ""
        echo "⚠️  This runs continuously until stopped (Ctrl+C)"
        echo ""
        read -p "Continue? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            python daily_scheduler.py
        else
            echo "Cancelled."
        fi
        ;;
    7)
        echo ""
        echo "🧪 Testing API Connection..."
        
        # Test if backend is running
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ Backend API is running"
            echo "   📍 Health check: http://localhost:8000/health"
            echo "   📚 API docs: http://localhost:8000/docs"
        else
            echo "❌ Backend API is not running"
            echo "   Start it with option 4 or 5"
        fi
        
        # Test database connection
        echo ""
        echo "Testing database connection..."
        python -c "
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('❌ DATABASE_URL not found')
else:
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM funding_opportunities;')
        count = cursor.fetchone()[0]
        print(f'✅ Database connected: {count} funding opportunities')
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
"
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-7."
        exit 1
        ;;
esac

echo ""
echo "🎉 Demo setup complete!"
echo ""
echo "💡 Demo Tips:"
echo "   - Use the '🇷🇼 Rwanda Demo' page in Streamlit for live demonstration"
echo "   - Search for 'Rwanda', 'AI', or 'health' to find relevant opportunities"
echo "   - Check the Dashboard for real-time statistics"
echo "   - API documentation available at http://localhost:8000/docs"
echo ""
echo "🇷🇼 Ready for Rwanda presentation!"
