#!/bin/bash
# Setup script for AI Africa Funding Tracker daily automation

PROJECT_DIR="/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker"
PLIST_FILE="$PROJECT_DIR/scripts/automation/ai.africa.funding.tracker.daily.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🚀 Setting up AI Africa Funding Tracker daily automation..."

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Copy plist to LaunchAgents directory
echo "📋 Installing daily collection job..."
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Load the job
echo "⚡ Loading daily collection job..."
launchctl load "$LAUNCH_AGENTS_DIR/ai.africa.funding.tracker.daily.plist"

# Check if job is loaded
echo "🔍 Checking job status..."
launchctl list | grep ai.africa.funding.tracker.daily

echo ""
echo "✅ Daily automation setup complete!"
echo ""
echo "📅 Schedule: Daily at 9:00 AM"
echo "🌍 Location: Alternates between London (odd days) and New York (even days)"
echo "📊 Logs: $PROJECT_DIR/logs/"
echo ""
echo "📋 Management commands:"
echo "  • Test run:     cd $PROJECT_DIR && source venv/bin/activate && python scripts/automation/daily_collector.py daily"
echo "  • Stop job:     launchctl unload $LAUNCH_AGENTS_DIR/ai.africa.funding.tracker.daily.plist"
echo "  • Start job:    launchctl load $LAUNCH_AGENTS_DIR/ai.africa.funding.tracker.daily.plist"
echo "  • Check status: launchctl list | grep ai.africa.funding.tracker.daily"
echo ""

# Offer to run a test
read -p "🧪 Would you like to run a test collection now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running test collection..."
    cd "$PROJECT_DIR"
    source venv/bin/activate
    python scripts/automation/daily_collector.py daily
    echo "✅ Test collection completed!"
fi

echo "🎉 Setup complete! Daily automation is now active."
