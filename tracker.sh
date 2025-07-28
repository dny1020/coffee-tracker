#!/bin/bash

API="https://coffee.newsbot.lat"
AUTH="Authorization: Bearer $API_KEY"

log_bpm() {
  read -p "BPM: " bpm
  read -p "Contexto (ej: post-café, ejercicio): " context
  curl -s -X POST "$API/heartrate/" \
    -H "$AUTH" -H "Content-Type: application/json" \
    -d "{\"bpm\": $bpm, \"context\": \"$context\"}" | jq
}

log_caffeine() {
  read -p "Cafeína (mg): " caffeine
  read -p "Tipo de café (ej: espresso, americano): " coffee_type
  curl -s -X POST "$API/coffee/" \
    -H "$AUTH" -H "Content-Type: application/json" \
    -d "{\"caffeine_mg\": $caffeine, \"coffee_type\": \"$coffee_type\"}" | jq
}

status_report() {
  echo "--- Último BPM ---"
  curl -s -H "$AUTH" "$API/heartrate/current" | jq
  echo "--- Último Café ---"
  curl -s -H "$AUTH" "$API/coffee/today" | jq
  echo "--- Correlación ---"
  curl -s -H "$AUTH" "$API/heartrate/correlation?hours_after=3" | jq
}

echo "¿Qué quieres hacer?"
select opt in "Log BPM" "Log Cafeína" "Ver Estado Actual" "Salir"; do
  case $opt in
    "Log BPM") log_bpm ;;
    "Log Cafeína") log_caffeine ;;
    "Ver Estado Actual") status_report ;;
    "Salir") exit ;;
    *) echo "Opción inválida" ;;
  esac
done

