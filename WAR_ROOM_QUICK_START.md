# War Room Quick Start Guide

## 🚀 Launch in 3 Steps

### 1. Start Backend
```bash
cd backend
python main.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Open War Room
Navigate to: `http://localhost:3000/warroom`

OR click **"Launch War Room"** button in dashboard header

---

## 🎯 What You'll See

### Immediate (0-5 seconds)
- ✓ Connection established
- ✓ "Pipeline initializing..." message
- ✓ First source starts scraping

### Early (5-30 seconds)
- 📊 Posts streaming in from each source
- 📈 Category breakdown updating
- ✅ Sources completing one by one
- 🔢 Signal counter incrementing

### Mid (30-60 seconds)
- 🤖 "AI processing signals..." status
- ⭐ Insights appearing in feed
- 📊 Category distribution stabilizing

### Final (60-90 seconds)
- 💯 Pulse score animating to final value
- 🚨 Alert banner (if anomaly detected)
- ✓ "Pipeline complete" message
- 🔘 "View Full Digest" button appears

---

## 🎬 Demo Script (For Presentations)

### Setup (Before Demo)
```bash
# Terminal 1
cd backend && python main.py

# Terminal 2  
cd frontend && npm run dev

# Browser
# Open http://localhost:3000
# Keep War Room tab ready
```

### During Demo
1. **"Let me show you our real-time intelligence system"**
   - Click "Launch War Room" button
   
2. **"Watch as we scrape multiple sources simultaneously"**
   - Point to feed as posts appear
   - Highlight different sources (HN, Google News, etc.)
   
3. **"Each signal is automatically categorized"**
   - Point to category breakdown chart
   - Show competitor vs. trend vs. pain point distribution
   
4. **"Our AI processes these in real-time"**
   - Wait for insights to appear
   - Read one or two insights aloud
   
5. **"The system calculates a pulse score"**
   - Watch animation complete
   - Explain what the score means
   
6. **"And alerts us to anomalies"** (if alert appears)
   - Point to red alert banner
   - Explain spike detection
   
7. **"All of this data is saved to our database"**
   - Click "View Full Digest"
   - Show structured dashboard

**Total demo time: ~90 seconds**

---

## 🧪 Quick Test

### Test SSE Endpoint
```bash
cd backend
python test_warroom.py
```

Expected output:
```
Testing War Room SSE endpoint: http://localhost:5000/api/stream/warroom
Connecting to stream...
------------------------------------------------------------
✓ Connected successfully!
Receiving events:

[Event 1] data: {"type":"start","ts":"14:32:15","message":"Pipeline initializing..."}
[Event 2] data: {"type":"status","ts":"14:32:16","message":"Scraping Hacker News..."}
...
✓ Received 10 events successfully!
War Room SSE endpoint is working correctly.
```

### Test with curl
```bash
curl -N http://localhost:5000/api/stream/warroom
```

Should see streaming JSON events.

---

## 🐛 Common Issues

### "Connection lost" immediately
**Fix:** Backend not running
```bash
cd backend
python main.py
```

### No events appearing
**Fix:** Check backend logs
```bash
# Look for errors in terminal running main.py
# Common: Missing API keys in .env
```

### Frontend won't build
**Fix:** Install dependencies
```bash
cd frontend
npm install
npm run dev
```

### Port 5000 already in use
**Fix:** Change port
```bash
cd backend
FLASK_PORT=5001 python main.py
```

Then update frontend API calls to use port 5001.

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| Total pipeline time | 60-90 seconds |
| First signal appears | ~5 seconds |
| Sources scraped | 5 (HN, Google News, RSS, EdSurge, Product Hunt) |
| Typical signal count | 20-50 posts |
| AI insights generated | 5-15 insights |
| Pulse score range | 40-100 |

---

## 🎨 Visual Guide

### Feed Item Colors
- **Blue-gray** — Regular posts
- **Amber** — AI insights (★ prefix)
- **Red** — Alerts (🚨 prefix)
- **Green** — Status updates (✓ prefix)

### Source Status Icons
- **○** — Waiting
- **~** — Running
- **✓** — Complete

### Category Colors
- **Blue bars** — All categories use blue gradient
- **Width** — Proportional to count

---

## 🔧 Customization

### Change Event Speed
Edit `backend/api/warroom_routes.py`:
```python
time.sleep(0.3)  # Faster: 0.1, Slower: 0.5
```

### Change Max Feed Items
Edit `frontend/src/components/WarRoom.tsx`:
```typescript
return newFeed.slice(0, 100);  // Change 100 to desired max
```

### Change Anomaly Threshold
Edit `backend/api/warroom_routes.py`:
```python
return today_count > avg * 2  # Change 2 to desired multiplier
```

---

## 📱 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Esc` | Close War Room |
| `Ctrl+R` | Refresh page (restart stream) |

---

## ✅ Pre-Demo Checklist

- [ ] Backend running (`python main.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] Browser open to dashboard
- [ ] War Room button visible in header
- [ ] Test connection (`curl -N http://localhost:5000/api/stream/warroom`)
- [ ] .env file has all API keys
- [ ] Internet connection stable (for scraping)

---

## 🎯 Key Talking Points

1. **"Real-time intelligence"** — Not batch processing, live streaming
2. **"Multiple sources"** — HN, Google News, RSS, EdSurge, Product Hunt
3. **"AI-powered categorization"** — Automatic classification
4. **"Anomaly detection"** — Alerts when unusual activity detected
5. **"Production-ready"** — SSE is battle-tested technology
6. **"No external dependencies"** — Pure Flask + React

---

## 📞 Need Help?

1. Check `WAR_ROOM_DOCS.md` for detailed documentation
2. Review backend logs for errors
3. Check browser console for frontend errors
4. Verify all API keys in `.env` file
5. Test SSE endpoint with `test_warroom.py`

---

## 🚀 Next Steps

After War Room is working:
1. Customize colors/styling in `WarRoom.tsx`
2. Add more sources in `warroom_routes.py`
3. Adjust event pacing for your preference
4. Configure anomaly threshold
5. Add custom event types for your use case

**Enjoy your live intelligence dashboard! 🎉**
