# Apple Shortcuts Guide - Coffee Tracker API

## Quick Start

Log coffee and heart rate data to your API using Apple Shortcuts on iPhone/iPad/Mac.

---

## Prerequisites

1. **Your API Information**:
   - URL: `https://coffee.danilocloud.me`
   - API Key: Your secure API key from `.env` file

2. **Apple Shortcuts App**:
   - Pre-installed on iOS/iPadOS/macOS
   - Open "Shortcuts" app

---

## 🚀 Quick Setup (Copy-Paste Method)

### Step 1: Save Your API Key

Create a shortcut to store your API key securely:

1. Open Shortcuts app
2. Tap **"+"** to create new shortcut
3. Add action: **"Text"**
4. Enter your API key (from `.env` file)
5. Add action: **"Set Variable"**
6. Name it: `API_KEY`
7. Name shortcut: **"Get Coffee API Key"**
8. Save

---

## ☕ Log Coffee Shortcut

### Shortcut Steps:

**Name**: Log Coffee

**Actions**:
```
1. Ask for Input
   - Prompt: "How much caffeine (mg)?"
   - Type: Number
   - Default: 95

2. Set Variable
   - Name: CaffeineMg
   - Value: [Provided Input]

3. Ask for Input
   - Prompt: "Coffee type?"
   - Type: Text
   - Default: "espresso"

4. Set Variable
   - Name: CoffeeType
   - Value: [Provided Input]

5. Ask for Input (optional)
   - Prompt: "Notes?"
   - Type: Text
   - Allow Empty: Yes

6. Set Variable
   - Name: Notes
   - Value: [Provided Input]

7. Run Shortcut
   - Shortcut: "Get Coffee API Key"
   - Get Variable: API_KEY

8. Get Contents of URL
   - URL: https://coffee.danilocloud.me/coffee/
   - Method: POST
   - Headers:
     • Authorization: Bearer [API_KEY]
     • Content-Type: application/json
   - Request Body: JSON
     {
       "caffeine_mg": [CaffeineMg],
       "coffee_type": "[CoffeeType]",
       "notes": "[Notes]"
     }

9. Show Notification
   - Title: "☕ Coffee Logged!"
   - Body: "[CaffeineMg]mg - [CoffeeType]"
```

### JSON Request Body (formatted):

```json
{
  "caffeine_mg": 95,
  "coffee_type": "espresso",
  "notes": "morning boost"
}
```

---

## 💓 Log Heart Rate Shortcut

### Shortcut Steps:

**Name**: Log Heart Rate

**Actions**:
```
1. Ask for Input
   - Prompt: "Heart rate (BPM)?"
   - Type: Number
   - Default: 75

2. Set Variable
   - Name: BPM
   - Value: [Provided Input]

3. Ask for Input
   - Prompt: "Context?"
   - Type: Text
   - Default: "resting"
   - Suggestions: resting, active, post-coffee, exercise

4. Set Variable
   - Name: Context
   - Value: [Provided Input]

5. Ask for Input (optional)
   - Prompt: "Notes?"
   - Type: Text
   - Allow Empty: Yes

6. Set Variable
   - Name: Notes
   - Value: [Provided Input]

7. Run Shortcut
   - Shortcut: "Get Coffee API Key"
   - Get Variable: API_KEY

8. Get Contents of URL
   - URL: https://coffee.danilocloud.me/heartrate/
   - Method: POST
   - Headers:
     • Authorization: Bearer [API_KEY]
     • Content-Type: application/json
   - Request Body: JSON
     {
       "bpm": [BPM],
       "context": "[Context]",
       "notes": "[Notes]"
     }

9. Show Notification
   - Title: "💓 Heart Rate Logged!"
   - Body: "[BPM] BPM - [Context]"
```

### JSON Request Body (formatted):

```json
{
  "bpm": 75,
  "context": "resting",
  "notes": "feeling good"
}
```

---

## 📋 API Endpoint Reference

### Coffee Endpoint

**URL**: `https://coffee.danilocloud.me/coffee/`  
**Method**: `POST`  
**Headers**:
```
Authorization: Bearer YOUR_API_KEY_HERE
Content-Type: application/json
```

**Request Body**:
```json
{
  "caffeine_mg": 95.0,
  "coffee_type": "espresso",
  "notes": "optional notes"
}
```

**Required Fields**:
- `caffeine_mg` (number, 0-1000)

**Optional Fields**:
- `coffee_type` (string, max 100 chars)
- `notes` (string, max 1000 chars)

**Response** (201 Created):
```json
{
  "id": 1,
  "caffeine_mg": 95.0,
  "coffee_type": "espresso",
  "notes": "optional notes",
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### Heart Rate Endpoint

**URL**: `https://coffee.danilocloud.me/heartrate/`  
**Method**: `POST`  
**Headers**:
```
Authorization: Bearer YOUR_API_KEY_HERE
Content-Type: application/json
```

**Request Body**:
```json
{
  "bpm": 75,
  "context": "resting",
  "notes": "optional notes"
}
```

**Required Fields**:
- `bpm` (integer, 30-250)

**Optional Fields**:
- `context` (string, max 50 chars): "resting", "active", "post-coffee", etc.
- `notes` (string, max 1000 chars)

**Response** (201 Created):
```json
{
  "id": 1,
  "bpm": 75,
  "context": "resting",
  "notes": "optional notes",
  "timestamp": "2025-10-04T12:00:00Z"
}
```

---

## 🎯 Common Coffee Types & Caffeine

Use these as presets in your shortcuts:

| Coffee Type | Typical Caffeine (mg) |
|-------------|----------------------|
| Espresso (single) | 63 |
| Espresso (double) | 126 |
| Americano | 95 |
| Latte | 95 |
| Cappuccino | 95 |
| Drip Coffee (8oz) | 95 |
| French Press | 107 |
| Cold Brew | 200 |
| Energy Drink | 80-160 |
| Tea (black) | 47 |
| Tea (green) | 28 |

---

## 🎨 Advanced Shortcuts

### Quick Log Coffee (Preset Values)

For your regular coffee:

```
1. Text: 95
2. Set Variable: CaffeineMg
3. Text: "espresso"
4. Set Variable: CoffeeType
5. Run Shortcut: "Get Coffee API Key"
6. Get Contents of URL
   - URL: https://coffee.danilocloud.me/coffee/
   - Method: POST
   - Headers: [Same as above]
   - Body: {"caffeine_mg": [CaffeineMg], "coffee_type": "[CoffeeType]"}
7. Show Notification: "Logged espresso!"
```

### Coffee Menu (Choose from List)

```
1. Choose from List
   - Prompt: "What did you drink?"
   - Items:
     • Espresso (63mg)
     • Double Espresso (126mg)
     • Americano (95mg)
     • Latte (95mg)
     • Cold Brew (200mg)

2. If [Chosen Item] is "Espresso"
   - Set Variable CaffeineMg = 63
   - Set Variable CoffeeType = "espresso"

3. If [Chosen Item] is "Double Espresso"
   - Set Variable CaffeineMg = 126
   - Set Variable CoffeeType = "double espresso"

[... repeat for each option]

4. Run Shortcut: "Get Coffee API Key"
5. Get Contents of URL [same as above]
6. Show Notification
```

### Auto-Log with Siri

**Setup**:
1. Create shortcut named **"Log Espresso"**
2. Add: Text → 95
3. Add: Set Variable → CaffeineMg
4. Add: Text → "espresso"
5. Add: Set Variable → CoffeeType
6. Add: API call (same as above)

**Use**:
- Say: "Hey Siri, Log Espresso"
- Logs automatically!

### Get Today's Caffeine Total

```
1. Run Shortcut: "Get Coffee API Key"
2. Get Contents of URL
   - URL: https://coffee.danilocloud.me/coffee/today
   - Method: GET
   - Headers: Authorization: Bearer [API_KEY]
3. Get Dictionary Value
   - Key: "total_caffeine_mg"
4. Show Notification
   - Title: "Today's Caffeine"
   - Body: "[total_caffeine_mg]mg consumed"
```

---

## 🔍 Troubleshooting

### Error: "Could not connect to server"

**Check**:
1. URL is correct: `https://coffee.danilocloud.me`
2. You have internet connection
3. Server is running

**Test**:
```bash
curl https://coffee.danilocloud.me/health
```

### Error: 401 Unauthorized

**Issue**: Wrong or missing API key

**Fix**:
1. Check API key in `.env` file
2. Update "Get Coffee API Key" shortcut
3. Make sure Authorization header is: `Bearer YOUR_KEY`

### Error: 422 Validation Error

**Issue**: Invalid data format

**Check**:
- Caffeine: Must be 0-1000
- Heart Rate: Must be 30-250
- JSON format is correct
- Content-Type header is `application/json`

### Error: SSL Certificate Error

**Issue**: HTTPS not properly configured

**Temporary Fix**:
- Use `http://` instead of `https://`
- ⚠️ Not secure! Fix SSL in production

---

## 📱 Widget Setup (iOS 14+)

Create a widget to log coffee quickly:

1. Add Shortcuts widget to home screen
2. Select "Log Coffee" shortcut
3. Tap widget → runs shortcut instantly!

---

## 🔐 Security Tips

1. **API Key**:
   - Keep it secret!
   - Don't share shortcuts containing the key
   - Rotate key periodically

2. **Use HTTPS**:
   - Always use `https://` not `http://`
   - Ensure SSL certificate is valid

3. **Shortcut Sharing**:
   - If sharing shortcuts, use "Get Coffee API Key" method
   - Don't hardcode API key in shared shortcuts

---

## 📊 Example Workflows

### Morning Routine

```
1. Log Coffee (espresso, 95mg)
2. Wait 30 minutes
3. Log Heart Rate
4. Get Today's Total
```

### Post-Workout

```
1. Log Heart Rate (context: "exercise")
2. Wait 15 minutes
3. Log Heart Rate (context: "recovery")
```

### Track Caffeine Impact

```
1. Log Heart Rate (before coffee)
2. Log Coffee
3. Wait 30 min
4. Log Heart Rate (post-coffee)
5. Compare readings
```

---

## 🎓 Quick Reference

### Coffee Endpoint
```
POST https://coffee.danilocloud.me/coffee/
Headers: Authorization: Bearer KEY, Content-Type: application/json
Body: {"caffeine_mg": 95, "coffee_type": "espresso", "notes": ""}
```

### Heart Rate Endpoint
```
POST https://coffee.danilocloud.me/heartrate/
Headers: Authorization: Bearer KEY, Content-Type: application/json
Body: {"bpm": 75, "context": "resting", "notes": ""}
```

### Get Today's Data
```
GET https://coffee.danilocloud.me/coffee/today
Headers: Authorization: Bearer KEY
```

---

## 📞 Need Help?

- Check API documentation: `https://coffee.danilocloud.me/docs`
- Test endpoint: `https://coffee.danilocloud.me/health`
- View OpenAPI spec: `https://coffee.danilocloud.me/openapi.json`

---

**Happy tracking! ☕💓**
