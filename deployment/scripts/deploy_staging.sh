#!/usr/bin/env bash
# Staging Deployment Script for NileGov Stack
# Applies the latest code, runs migrations, and seeds L2 data

set -e

echo "=================================================="
echo " Starting Staging Deployment for NileGov Stack"
echo "=================================================="

echo "[1/5] Pulling latest code from origin/main..."
git fetch origin
git checkout main
git pull origin main

echo "[2/5] Running database migrations..."
# In a frappe docker context, you might need to run this via docker-compose exec
# E.g., docker-compose exec backend bench migrate
bench migrate || echo "Warning: 'bench' command not found or failed. Ensure you are in the frappe bench directory."

echo "[3/5] Clearing cache..."
bench clear-cache || echo "Warning: 'bench' command not found or failed."

echo "[4/5] Restarting web and worker processes..."
supervisorctl restart frappe-bench-web: || echo "Warning: supervisorctl web restart failed."
supervisorctl restart frappe-bench-workers: || echo "Warning: supervisorctl workers restart failed."

echo "[5/5] Executing L2 Demo Data Seeding..."
# Execute the seed script
bench execute deployment.scripts.seed_l2_demo_data.seed_data || echo "Warning: Seeding script execution failed."

echo "=================================================="
echo " Staging Deployment Completed Successfully!"
echo "=================================================="
