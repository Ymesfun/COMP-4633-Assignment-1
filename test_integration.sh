#!/bin/bash
API_URL="http://[YOUR_VM_PUBLIC_IP_HERE]:5000/api/v1"

echo "=== 1. RETRIEVAL: List all events ==="
curl -X GET "$API_URL/events" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 2. RETRIEVAL: Get specific event (Event 1) ==="
curl -X GET "$API_URL/events/1" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 3. CREATION: Add a new event ==="
curl -X POST "$API_URL/events" \
     -H "Content-Type: application/json" \
     -d '{"title": "Senior Social", "location":"Lincoln park", "start_datetime":"2027-01-12 16:00:00", "capacity": 12}'
echo -e "\n\n"

echo "=== 4. MODIFICATION: Update event 1 capacity ==="
curl -X PATCH "$API_URL/events/1" \
     -H "Content-Type: application/json" \
     -d '{"capacity": 20}'
echo -e "\n\n"

echo "=== 5. DELETION: Delete event 3 ==="
curl -X DELETE "$API_URL/events/3" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 6. SUCCESSFUL BOOKING: Register participant 4 for event 1 ==="
curl -X POST "$API_URL/registrations/" \
     -H "Content-Type: application/json" \
     -d '{"event_id": 1, "participant_id": 4}'
echo -e "\n\n"

echo "=== 7. REJECTED BOOKING: Try duplicate registration ==="
curl -X POST "$API_URL/registrations/" \
     -H "Content-Type: application/json" \
     -d '{"event_id": 1, "participant_id": 4}'
echo -e "\n\n"

echo "=== 8. RETRIEVAL: List registrations for event 1 ==="
curl -X GET "$API_URL/registrations/?event_id=1" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 9. CANCELLATION: Cancel registration ID 1 ==="
curl -X DELETE "$API_URL/registrations/1" -H "Content-Type: application/json"
echo -e "\n\n"

echo "=== 10. RETRIEVAL (Post-Cancel): List registrations for event 1 ==="
curl -X GET "$API_URL/registrations/?event_id=1" -H "Content-Type: application/json"
echo -e "\n"