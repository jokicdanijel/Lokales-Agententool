#!/usr/bin/env bash
# Test opena_finance REST API
# Usage: bash test_opena_finance.sh

set -euo pipefail

BASE_URL="http://127.0.0.1:12347"
TOKEN=$(head -1 .env | cut -d= -f2 2>/dev/null || echo "MEIN_SUPER_TOKEN_123")

echo "🧪 Testing opena_finance API..."
echo "Token: $TOKEN"
echo ""

# 1. Health Check
echo "1️⃣  Health Check..."
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. Create Account
echo "2️⃣  Create Account (Savings)..."
ACCOUNT=$(curl -s -X POST "$BASE_URL/account/create?name=Savings&account_type=savings&initial_balance=5000&currency=EUR" \
  -H "Authorization: Bearer $TOKEN" | jq .)
ACCOUNT_ID=$(echo "$ACCOUNT" | jq -r '.id')
echo "$ACCOUNT" | jq .
echo ""

# 3. List Accounts
echo "3️⃣  List Accounts..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/accounts" | jq .
echo ""

# 4. Add Transaction (Income)
echo "4️⃣  Add Transaction (Income +200)..."
curl -s -X POST "$BASE_URL/transaction/add?account_id=$ACCOUNT_ID&amount=200&description=Salary&category=income" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 5. Add Transaction (Expense)
echo "5️⃣  Add Transaction (Expense -100)..."
curl -s -X POST "$BASE_URL/transaction/add?account_id=$ACCOUNT_ID&amount=-100&description=Rent&category=expense" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 6. List Transactions
echo "6️⃣  List Transactions..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/transactions?account_id=$ACCOUNT_ID" | jq .
echo ""

# 7. Generate Statement
echo "7️⃣  Generate Statement..."
STMT=$(curl -s -X POST "$BASE_URL/statement/generate?account_id=$ACCOUNT_ID&period_days=30" \
  -H "Authorization: Bearer $TOKEN" | jq .)
STMT_ID=$(echo "$STMT" | jq -r '.id')
echo "$STMT" | jq .
echo ""

# 8. Fetch Statement
echo "8️⃣  Fetch Statement..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/statement/$STMT_ID" | jq .
echo ""

# 9. Dashboard Summary
echo "9️⃣  Dashboard Summary..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/dashboard" | jq .
echo ""

echo "✅ All tests passed!"
