#!/bin/bash

# Sales Agent Setup Script

echo "================================"
echo "Sales Agent - Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if PostgreSQL is installed
echo ""
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is installed"
else
    echo "✗ PostgreSQL is not installed. Please install PostgreSQL 12+"
    exit 1
fi

# Check if Redis is installed
echo ""
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis is installed"
else
    echo "✗ Redis is not installed. Please install Redis 6+"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo ""
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file already exists"
fi

# Create database
echo ""
echo "Setting up database..."
read -p "Create database? (y/n): " create_db

if [ "$create_db" = "y" ]; then
    read -p "PostgreSQL username [postgres]: " db_user
    db_user=${db_user:-postgres}

    read -p "Database name [salesagent]: " db_name
    db_name=${db_name:-salesagent}

    echo "Creating database $db_name..."
    createdb -U $db_user $db_name 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ Database created successfully"
    else
        echo "⚠️  Database may already exist or creation failed"
    fi
fi

# Initialize database tables
echo ""
echo "Initializing database tables..."
python3 -c "from models import init_db; init_db(); print('✓ Database tables created')"

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - APOLLO_API_KEY"
echo "   - EMAIL credentials"
echo ""
echo "2. Start Redis:"
echo "   redis-server"
echo ""
echo "3. Start Celery worker:"
echo "   celery -A worker.celery_app worker --loglevel=info"
echo ""
echo "4. Start API server:"
echo "   python main.py"
echo ""
echo "5. Visit http://localhost:8000/docs for API documentation"
echo ""
