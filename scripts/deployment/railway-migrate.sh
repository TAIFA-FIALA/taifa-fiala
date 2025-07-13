#!/bin/bash

# TAIFA-FIALA Railway Database Migration Script
# Runs database migrations and initial setup on Railway

set -e

echo "🚄 TAIFA Railway Database Migration Starting..."

# Check if DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not found"
    exit 1
fi

echo "✅ Database URL configured"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until pg_isready -d "$DATABASE_URL"; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done

echo "✅ Database is ready"

# Run Alembic migrations
echo "🔄 Running database migrations..."
cd /app/backend
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Initialize default data if needed
echo "📊 Checking for initial data setup..."

python -c "
import os
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if we have any funding opportunities
    cursor.execute('SELECT COUNT(*) as count FROM funding_opportunities;')
    count = cursor.fetchone()['count']
    
    print(f'Current funding opportunities in database: {count}')
    
    if count == 0:
        print('📋 No funding opportunities found. Database is ready for first collection.')
    else:
        print('✅ Database already contains funding opportunities.')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'⚠️  Database check failed: {e}')
    print('Database structure may need to be created.')
"

echo "🎉 Railway database migration complete!"
echo "📝 Next steps:"
echo "   1. Deploy backend service"
echo "   2. Deploy frontend service" 
echo "   3. Deploy data collection service"
echo "   4. Configure custom domains"
