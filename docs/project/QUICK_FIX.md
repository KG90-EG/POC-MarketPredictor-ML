# Quick Fix für alle aktuellen Probleme

## Problem 1: Network Error & Alte Watchlists

**Ursache**: Browser-Cache lädt alte Version ohne CURRENT_USER_ID

**Lösung**:

```bash
# Im Browser (Chrome DevTools):
1. F12 öffnen
2. Application Tab
3. Local Storage → http://localhost:5174
4. ALLES löschen (Clear All)
5. Seite mit Cmd+Shift+R neu laden (Hard Reload)
```

## Problem 2: apiClient.post is not a function

**Ursache**: Import war falsch (bereits gefixt)

**Status**: ✅ BEHOBEN - Import jetzt `import { apiClient } from '../api'`

## Problem 3: Simulator & Buy Button bläulich

**Ursache**: CSS wird nicht neu geladen oder tabs haben immer active class

**Lösung**:

```bash
# Frontend neu bauen
cd frontend
npm run build
cd ..
# Browser Hard Reload: Cmd+Shift+R
```

## Schnelle Lösung - Alles auf einmal

```bash
# 1. Backend & Frontend neu starten
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
sleep 2

# 2. Backend starten
cd /Users/kevingarcia/Documents/POC-MarketPredictor-ML
.venv/bin/python -m uvicorn trading_fun.server:app --host 0.0.0.0 --port 8000 --reload &

# 3. Frontend neu bauen und starten
cd frontend
npm run build
npm run dev &

# 4. Warten
sleep 5

echo "✓ Server neu gestartet"
echo "→ Jetzt Browser öffnen: http://localhost:5174"
echo "→ F12 → Application → Local Storage → Clear All"
echo "→ Cmd+Shift+R (Hard Reload)"
```

## Was du im Browser machen musst

1. **F12** drücken (DevTools öffnen)
2. **Application** Tab wählen
3. **Local Storage** → **<http://localhost:5174>** anklicken
4. Rechtsklick → **Clear** (oder Clear All Button oben)
5. **Cmd+Shift+R** (Mac) oder **Ctrl+Shift+R** (Windows) für Hard Reload

## Warum diese Probleme?

- **Alte Watchlists**: localStorage hatte keine user_id, nutzt noch "default_user"
- **Network Error**: Frontend cached alte API-Version ohne neue CURRENT_USER_ID
- **Bläuliche Buttons**: CSS-Cache oder React State Problem
- **apiClient Error**: Import wurde nicht aktualisiert (jetzt gefixt)

## Nach dem Fix solltest du sehen

- ✅ Keine alten Watchlists
- ✅ Neue unique user_id in localStorage (`market_predictor_user_id`)
- ✅ Simulator Button grün und funktioniert
- ✅ Buy/Sell Tabs nicht permanent blau
- ✅ Keine Network Errors
