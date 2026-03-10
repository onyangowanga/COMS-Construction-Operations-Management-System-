#!/bin/bash

# Setup GitHub Token for Private Repository Access
# Run this AFTER initial deployment and BEFORE making repo private

echo "================================"
echo "GitHub Token Setup for VPS"
echo "================================"

# Get token from user
echo ""
echo "First, create a GitHub Personal Access Token:"
echo "1. Go to: https://github.com/settings/tokens/new"
echo "2. Name: COMS VPS Access"
echo "3. Expiration: No expiration (or 1 year)"
echo "4. Scopes: Check 'repo' (all repository permissions)"
echo "5. Generate token"
echo ""
read -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN

# Configure git to use the token
cd /root/coms

# Set the remote URL with token embedded
git remote set-url origin https://${GITHUB_TOKEN}@github.com/onyangowanga/COMS-Construction-Operations-Management-System-.git

echo ""
echo "✅ GitHub authentication configured!"
echo "You can now make your repository private."
echo "Auto-deployment will continue to work."
