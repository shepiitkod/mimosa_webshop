#!/bin/bash
# Pre-deployment verification script for Mimosa WebShop
# Run this locally before pushing to Render

echo "🔍 Mimosa WebShop - Pre-Deployment Audit Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES=0

# Detect Python interpreter once and reuse it in all checks.
if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN=""
fi

# Check Python version
echo "1️⃣  Checking Python version..."
if [ -n "$PYTHON_BIN" ]; then
    "$PYTHON_BIN" --version || { echo -e "${RED}❌ Python found but not runnable${NC}"; ISSUES=$((ISSUES+1)); }
else
    echo -e "${RED}❌ Python not found (install python3)${NC}"
    ISSUES=$((ISSUES+1))
fi
echo ""

# Check if venv is activated
echo "2️⃣  Checking virtual environment..."
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected. Activate it: source .venv/bin/activate${NC}"
else
    echo -e "${GREEN}✅ Using: $VIRTUAL_ENV${NC}"
fi
echo ""

# Check requirements
echo "3️⃣  Verifying critical dependencies..."
PACKAGES=("dj_database_url" "psycopg2" "gunicorn" "whitenoise" "django")
for pkg in "${PACKAGES[@]}"; do
    if [ -n "$PYTHON_BIN" ] && "$PYTHON_BIN" -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}✅ $pkg${NC}"
    else
        echo -e "${RED}❌ $pkg missing${NC}"
        ISSUES=$((ISSUES+1))
    fi
done
echo ""

# Check Django settings
echo "4️⃣  Checking Django settings..."
if [ -n "$PYTHON_BIN" ]; then
    "$PYTHON_BIN" manage.py check >/dev/null 2>&1 && echo -e "${GREEN}✅ Django configuration OK${NC}" || { echo -e "${RED}❌ Django check failed${NC}"; ISSUES=$((ISSUES+1)); }
else
    echo -e "${RED}❌ Skipping Django check: Python not available${NC}"
    ISSUES=$((ISSUES+1))
fi
echo ""

# Check for {% load static %}
echo "5️⃣  Verifying {% load static %} in templates..."
TEMPLATES_WITHOUT_LOAD=$(find templates -name "*.html" -exec grep -L "{% load static %}" {} \; 2>/dev/null | grep -v "footer\|header")
if [ -z "$TEMPLATES_WITHOUT_LOAD" ]; then
    echo -e "${GREEN}✅ All templates have {% load static %}${NC}"
else
    echo -e "${RED}❌ Templates missing {% load static %}:${NC}"
    echo "$TEMPLATES_WITHOUT_LOAD"
    ISSUES=$((ISSUES+1))
fi
echo ""

# Check staticfiles collected
echo "6️⃣  Checking static files collection..."
if [ -d "staticfiles" ]; then
    echo -e "${GREEN}✅ staticfiles/ directory exists${NC}"
else
    echo -e "${YELLOW}⚠️  staticfiles/ not found. Run: python manage.py collectstatic --noinput${NC}"
fi
echo ""

# Check .env file
echo "7️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
    if grep -q "DJANGO_SECRET_KEY=" .env && grep -q "DATABASE_URL=" .env; then
        echo -e "${GREEN}✅ Required env vars present${NC}"
    else
        echo -e "${RED}❌ Missing required env vars in .env${NC}"
        ISSUES=$((ISSUES+1))
    fi
elif [ -f ".env.example" ]; then
    echo -e "${YELLOW}⚠️  .env not found, but .env.example exists${NC}"
    echo "     Copy: cp .env.example .env"
    echo "     Edit .env with your configuration"
else
    echo -e "${RED}❌ Neither .env nor .env.example found${NC}"
    ISSUES=$((ISSUES+1))
fi
echo ""

# Check database migrations
echo "8️⃣  Checking database migrations..."
if [ -n "$PYTHON_BIN" ]; then
    PENDING=$($PYTHON_BIN manage.py showmigrations --plan 2>/dev/null | grep -c "\[X\]" || echo "0")
else
    PENDING="0"
fi
if [ "$PENDING" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  No migrations marked as applied. Run: ${PYTHON_BIN:-python3} manage.py migrate${NC}"
else
    echo -e "${GREEN}✅ Database migrations in place${NC}"
fi
echo ""

# Check Procfile
echo "9️⃣  Checking Procfile for Render..."
if grep -q "gunicorn mimosa_backend.wsgi" Procfile 2>/dev/null; then
    echo -e "${GREEN}✅ Procfile configured correctly${NC}"
else
    echo -e "${RED}❌ Procfile not configured for Render${NC}"
    ISSUES=$((ISSUES+1))
fi
echo ""

# Summary
echo "================================================"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for Render deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Push to GitHub"
    echo "2. Connect to Render.com"
    echo "3. Set environment variables on Render dashboard"
    echo "4. Deploy!"
else
    echo -e "${RED}❌ Found $ISSUES issue(s). Please fix before deploying.${NC}"
fi
echo ""
