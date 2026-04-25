# SSML Quick Reference

## ✅ What Was Fixed

### Before
- TTS engines read `<break>` and `<prosody>` as plain text
- No fallback for unsupported engines
- Single output format (SSML only)

### After
- ✅ Dual output: SSML + Plain text
- ✅ Auto-detection of engine capability
- ✅ Graceful fallback to plain text
- ✅ Natural pauses using punctuation in plain text

## 🎯 Key Files Modified

```
backend/processor/ssml_converter.py    ← Core converter (NEW)
backend/api/routes.py                  ← Added /api/voice-script endpoint
frontend/src/lib/api.ts                ← Added fetchVoiceScript()
frontend/src/components/VoiceDigest.tsx ← SSML detection + version selection
```

## 🚀 Quick Start

### Backend
```python
from processor.ssml_converter import SSMLConverter

converter = SSMLConverter()
result = converter.convert(digest)

# Returns:
# {
#   "ssml": "<speak>...</speak>",
#   "plain_text": "Good morning..."
# }
```

### Frontend
```typescript
const response = await fetchVoiceScript();
const script = ssmlSupported ? response.ssml : response.plain_text;
```

### API
```bash
curl http://localhost:5000/api/voice-script
```

## 📋 Output Format

### SSML (for Google voices, AWS Polly, etc.)
```xml
<speak>
<prosody rate="0.95" pitch="-2%">
Good morning. <break time="500ms"/>
Here's your briefing...
</prosody>
</speak>
```

### Plain Text (for Safari, Firefox, etc.)
```
Good morning.

Here's your briefing...
```

## 🎨 Pause Mapping

| SSML | Plain Text | Use Case |
|------|------------|----------|
| `<break time="300ms"/>` | ` ` (space) | Between sentences |
| `<break time="500ms"/>` | ` ` (space) | Between items |
| `<break time="600ms"/>` | `\n\n` (double newline) | Between sections |

## 🔧 Configuration

### Content Limits (in ssml_converter.py)
```python
competitors[:3]   # Max 3 competitor updates
trends[:3]        # Max 3 emerging trends
pain_points[:2]   # Max 2 user pain points
```

### Sentence Length
```python
max_words = 15    # Max words per sentence
```

### Speech Rate
```python
rate="0.95"       # 95% of normal speed
pitch="-2%"       # Slightly lower pitch
```

## ✨ Features

1. **Text Cleaning**
   - Removes markdown: `*`, `_`, `#`, `` ` ``
   - Converts: `&` → "and", `%` → "percent", `/` → " or "
   - Strips URLs and links

2. **Sentence Shortening**
   - Splits at punctuation or 15 words
   - Ensures complete sentences
   - No cut-off phrases

3. **Natural Transitions**
   - "Let's start with competitor updates"
   - "Now for emerging trends"
   - "Here's what users are saying"

4. **Professional Tone**
   - Calm, confident delivery
   - Executive briefing style
   - No hype or casual language

## 🧪 Testing

```bash
# Test the converter
python3 test_ssml_standalone.py

# Expected output:
# ✅ ALL CHECKS PASSED!
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Tags read as text | System auto-uses plain text version |
| Voice too fast | Adjust `rate="0.95"` in `_build_ssml()` |
| Pauses too long | Reduce break times (300/500/600ms) |
| Content too long | Reduce item limits (3/3/2) |

## 📊 Browser Support

- **Chrome**: Uses SSML (Google voices detected)
- **Safari**: Uses plain text (no SSML support)
- **Firefox**: Uses plain text (no SSML support)
- **Edge**: Uses plain text (safer fallback)

## 🎯 Next Steps

1. Start backend: `cd backend && python3 main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open dashboard and click "Play" on Morning Brief
4. System auto-detects and uses correct version

## 💡 Pro Tips

- Plain text version uses natural punctuation for pauses
- SSML version provides precise timing control
- Both versions sound natural and professional
- No manual switching needed - fully automatic
