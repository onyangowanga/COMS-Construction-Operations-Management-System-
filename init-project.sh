#!/bin/bash
# init-project.sh - Initialize Django COMS Project

echo "🚀 Initializing COMS Project..."

# Create Django project if manage.py doesn't exist
if [ ! -f "manage.py" ]; then
    echo "📦 Creating Django project..."
    django-admin startproject config .
fi

# Create apps directory
mkdir -p apps

# Create core Django apps
apps=("authentication" "projects" "ledger" "workers" "consultants" "clients" "core")

for app in "${apps[@]}"
do
    if [ ! -d "apps/$app" ]; then
        echo "📂 Creating app: $app"
        python manage.py startapp $app apps/$app
    fi
done

# Create static and media directories
mkdir -p static staticfiles media/uploads/{documents,drawings,photos}

# Create templates directory
mkdir -p templates/{authentication,projects,ledger,workers,consultants,clients,base}

# Create logs directory
mkdir -p logs

# Run initial migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
echo "✅ Project initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and update values"
echo "2. Run: python manage.py createsuperuser"
echo "3. Start development server: python manage.py runserver"
