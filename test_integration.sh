#!/bin/bash
API_URL="http://[YOUR_VM_PUBLIC_IP_HERE]:5000/api/v1"

echo "=== 1. RETRIEVAL: List all events ==="
curl -X GET "$API_URL/events" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 2. SUCCESSFUL BOOKING: Register participant 4 for event 1 ==="
curl -X POST "$API_URL/registrations/" \
     -H "Content-Type: application/json" \
     -d '{"event_id": 1, "participant_id": 4}'
echo -e "\n\n"

echo "=== 3. REJECTED BOOKING: Try duplicate registration ==="
curl -X POST "$API_URL/registrations/" \
     -H "Content-Type: application/json" \
     -d '{"event_id": 1, "participant_id": 4}'
echo -e "\n\n"

echo "=== 4. RETRIEVAL: List registrations for event 1 ==="
curl -X GET "$API_URL/registrations/?event_id=1" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 5. CANCELLATION: Cancel registration ID 1 ==="
curl -X DELETE "$API_URL/registrations/1" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 6. RETRIEVAL (Post-Cancel): List registrations for event 1 ==="
curl -X GET "$API_URL/registrations/?event_id=1" -H "Content-Type: application/json"
echo -e "\n"