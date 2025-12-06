#!/bin/bash

echo "============================================================"
echo "Starting BlockStat Pro Backend Server"
echo "============================================================"
echo ""

cd backend

echo "Checking dependencies..."
npm install

echo ""
echo "Starting server..."
echo ""
npm run dev

