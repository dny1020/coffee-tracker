# Apple Shortcuts Guide - Coffee Tracker API

## Quick Start

Log coffee and heart rate data to your Coffee Tracker API using Apple Shortcuts on iPhone/iPad/Mac.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: Simple Setup (Recommended)](#method-1-simple-setup-recommended)
3. [Method 2: Advanced Setup with Variables](#method-2-advanced-setup-with-variables)
4. [Testing Your Shortcuts](#testing-your-shortcuts)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need:

1. **Your API Information**:
   - **Base URL**: `https://coffee.danilocloud.me` (or your custom domain)
   - **API Key**: From your `.env` file (look for `API_KEY=...`)

2. **Apple Shortcuts App**:
   - Pre-installed on iOS 13+, iPadOS 13+, macOS 12+
   - If deleted, download from App Store

3. **Network Access**:
   - iPhone/iPad/Mac must have internet connection
   - API must be accessible from your device

---

## Method 1: Simple Setup (Recommended)

This method is the easiest and works great for most users.

### ☕ Log Coffee Shortcut

#### Step-by-Step Instructions:

1. **Open Shortcuts App** on your iPhone/iPad/Mac

2. **Create New Shortcut**:
   - Tap **"+"** button (top right)
   - Or tap **"Create Shortcut"**

3. **Add "Get Contents of URL" Action**:
   - Tap **"Add Action"**
   - Search for **"Get Contents of URL"**
   - Tap to add it

4. **Configure the Request**:
   - **URL**: `https://coffee.danilocloud.me/coffee/`
   - Tap **"Show More"** to expand options
   - **Method**: `POST`
   - **Headers**:
     - Add header: `Authorization` = `Bearer YOUR_API_KEY_HERE`
       (Replace `YOUR_API_KEY_HERE` with your actual API key from .env)
     - Add header: `Content-Type` = `application/json`
   - **Request Body**: `JSON`
   - **JSON**:
     ```json
     {
       "caffeine_mg": 120,
       "coffee_type": "espresso",
       "notes": "Morning coffee"
     }
     ```

5. **Add "Show Result" Action** (optional):
   - Search for **"Show Result"**
   - This will display the API response

6. **Name Your Shortcut**:
   - Tap the shortcut name at top
   - Rename to **"Log Coffee"**

7. **Save**: Tap **"Done"**

#### Making It Interactive:

To ask for caffeine amount each time:

1. **Before** the "Get Contents of URL" action, add:
   - Action: **"Ask for Input"**
   - Prompt: `"How much caffeine (mg)?"`
   - Input Type: `Number`
   - Default Answer: `95`

2. **Update JSON** in "Get Contents of URL":
   ```json
   {
     "caffeine_mg": [Provided Input],
     "coffee_type": "coffee",
     "notes": "Logged via Shortcuts"
   }
   ```
   
   Note: Tap inside the JSON and select "Provided Input" variable from the variables menu

---

### ❤️ Log Heart Rate Shortcut

#### Step-by-Step Instructions:

1. **Create New Shortcut** (same as above)

2. **Add "Get Contents of URL" Action**:
   - **URL**: `https://coffee.danilocloud.me/heartrate/`
   - **Method**: `POST`
   - **Headers**:
     - `Authorization`: `Bearer YOUR_API_KEY_HERE`
     - `Content-Type`: `application/json`
   - **Request Body**: `JSON`
   - **JSON**:
     ```json
     {
       "bpm": 75,
       "context": "resting",
       "notes": "Logged via Shortcuts"
     }
     ```

3. **Add "Show Result" Action**

4. **Name**: **"Log Heart Rate"**

#### Making It Interactive:

Add before the URL action:

1. **Ask for Input**:
   - Prompt: `"What's your heart rate (BPM)?"`
   - Input Type: `Number`
   - Default: `75`

2. **Update JSON**:
   ```json
   {
     "bpm": [Provided Input],
     "context": "manual",
     "notes": "Logged via Shortcuts"
   }
   ```

---

## Method 2: Advanced Setup with Variables

This method stores your API key in one place for reuse across multiple shortcuts.

### Step 1: Create API Configuration Shortcut

1. **Create New Shortcut**

2. **Add "Dictionary" Action**:
   - Search for "Dictionary"
   - Configure:
     ```
     API_KEY: YOUR_API_KEY_HERE
     BASE_URL: https://coffee.danilocloud.me
     ```

3. **Name**: **"Coffee API Config"**

### Step 2: Create Log Coffee Shortcut (Advanced)

1. **Create New Shortcut**

2. **Get API Config**:
   - Add action: **"Run Shortcut"**
   - Select: **"Coffee API Config"**
   - Add action: **"Get Dictionary Value"**
   - Key: `API_KEY`
   - Add action: **"Set Variable"** → `api_key`

3. **Ask for Input**:
   - Prompt: `"How much caffeine (mg)?"`
   - Type: `Number`
   - Default: `95`
   - Set variable: `caffeine_amount`

4. **Ask for Coffee Type**:
   - Prompt: `"Coffee type?"`
   - Type: `Text`
   - Default: `"coffee"`
   - Set variable: `coffee_type`

5. **Get Contents of URL**:
   - URL: `https://coffee.danilocloud.me/coffee/`
   - Method: `POST`
   - Headers:
     - `Authorization`: `Bearer [api_key]`
     - `Content-Type`: `application/json`
   - Request Body: `JSON`
   - JSON:
     ```json
     {
       "caffeine_mg": [caffeine_amount],
       "coffee_type": [coffee_type],
       "notes": "Logged via Shortcuts"
     }
     ```

6. **Show Result**

7. **Name**: **"Log Coffee Advanced"**

---

## Testing Your Shortcuts

### Test 1: Basic Connectivity

Create a simple test shortcut:

1. Add "Get Contents of URL":
   - URL: `https://coffee.danilocloud.me/health`
   - Method: `GET`
2. Add "Show Result"
3. Run it

**Expected Result**: Should show JSON with `"status": "alive"`

### Test 2: Authentication

1. Add "Get Contents of URL":
   - URL: `https://coffee.danilocloud.me/coffee/today`
   - Method: `GET`
   - Headers: `Authorization`: `Bearer YOUR_API_KEY`
2. Add "Show Result"
3. Run it

**Expected Result**: Should show today's caffeine data or empty result

### Test 3: Post Data

Use your "Log Coffee" shortcut:

1. Run the shortcut
2. Enter caffeine amount (e.g., 120)
3. Check response

**Expected Success Response**:
```json
{
  "id": 123,
  "caffeine_mg": 120.0,
  "coffee_type": "coffee",
  "timestamp": "2024-10-05T10:30:00Z",
  "notes": "Logged via Shortcuts"
}
```

**Common Error Responses**:

- **401 Unauthorized**: Wrong API key
- **422 Validation Error**: Invalid caffeine amount (must be 0-1000)
- **500 Server Error**: Check API health

---

## Troubleshooting

### Issue: "The operation couldn't be completed"

**Cause**: Network connectivity or URL issue

**Fix**:
1. Check internet connection
2. Verify URL is correct: `https://coffee.danilocloud.me`
3. Try accessing URL in Safari first

### Issue: "401 Unauthorized"

**Cause**: Invalid or missing API key

**Fix**:
1. Check your `.env` file for the correct API key
2. Ensure header is exactly: `Authorization: Bearer YOUR_KEY`
   - Must have space between "Bearer" and the key
   - No extra quotes
3. Test with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
        https://coffee.danilocloud.me/coffee/today
   ```

### Issue: "422 Validation Error"

**Cause**: Data validation failed

**Fix**:

For **Coffee endpoint**:
- `caffeine_mg` must be 0-1000
- `coffee_type` max 100 characters
- `notes` max 1000 characters

For **Heart Rate endpoint**:
- `bpm` must be 30-250
- `context` max 50 characters
- `notes` max 1000 characters

### Issue: Response shows database error

**Cause**: API database issue

**Fix**:
1. Check API health: `https://coffee.danilocloud.me/health`
2. Contact server administrator
3. See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Issue: Shortcut times out

**Cause**: Slow network or API down

**Fix**:
1. Check if API is up: `https://coffee.danilocloud.me/health`
2. Try again with better connection
3. Increase timeout in "Get Contents of URL" advanced settings

---

## Example Shortcuts

### Quick Coffee Logger (Minimal)

**Actions**:
1. Get Contents of URL
   - URL: `https://coffee.danilocloud.me/coffee/`
   - Method: POST
   - Headers: `Authorization: Bearer YOUR_KEY`, `Content-Type: application/json`
   - Body: `{"caffeine_mg": 95, "coffee_type": "coffee"}`

### Coffee with Apple Watch Integration

**Actions**:
1. Get current date/time → Set variable `timestamp`
2. Ask for number: "Caffeine (mg)?"
3. Get Contents of URL (same as above, with input)
4. Show notification: "Coffee logged!"

### Heart Rate from Health App

**Actions**:
1. Get "Heart Rate" samples from Health
   - Latest sample
2. Get value from health sample
3. Set variable: `heart_rate`
4. Get Contents of URL:
   - URL: `https://coffee.danilocloud.me/heartrate/`
   - Method: POST
   - Headers: Auth + Content-Type
   - Body: `{"bpm": [heart_rate], "context": "health-app"}`
5. Show notification: "Heart rate logged!"

---

## API Endpoints Reference

### POST /coffee/

Log coffee consumption.

**Required Headers**:
- `Authorization: Bearer YOUR_API_KEY`
- `Content-Type: application/json`

**Request Body**:
```json
{
  "caffeine_mg": 120,          // Required: 0-1000
  "coffee_type": "espresso",   // Optional: max 100 chars
  "notes": "Morning coffee"    // Optional: max 1000 chars
}
```

**Response**:
```json
{
  "id": 123,
  "caffeine_mg": 120.0,
  "coffee_type": "espresso",
  "timestamp": "2024-10-05T10:30:00Z",
  "notes": "Morning coffee"
}
```

### POST /heartrate/

Log heart rate reading.

**Required Headers**:
- `Authorization: Bearer YOUR_API_KEY`
- `Content-Type: application/json`

**Request Body**:
```json
{
  "bpm": 75,                   // Required: 30-250
  "context": "resting",        // Optional: max 50 chars
  "notes": "After coffee"      // Optional: max 1000 chars
}
```

**Response**:
```json
{
  "id": 456,
  "bpm": 75,
  "context": "resting",
  "timestamp": "2024-10-05T10:35:00Z",
  "notes": "After coffee"
}
```

### GET /coffee/today

Get today's total caffeine.

**Response**:
```json
{
  "date": "2024-10-05",
  "total_caffeine_mg": 285.0,
  "addiction_level": "moderate addict",
  "recommended_max": 400,
  "over_limit": false
}
```

### GET /heartrate/current

Get latest heart rate reading.

**Response**:
```json
{
  "bpm": 75,
  "context": "resting",
  "timestamp": "2024-10-05T10:35:00Z",
  "minutes_ago": 5
}
```

---

## Security Best Practices

1. **Never share your API key** in screenshots or public shortcuts
2. **Use HTTPS** - Never use `http://`
3. **Rotate keys regularly** - Update API_KEY in .env and shortcuts
4. **Test in private** - Don't share shortcuts with embedded API keys
5. **Use Shortcut Privacy** - Mark shortcuts as private in iCloud

---

## Advanced: Automation Ideas

### Morning Coffee Routine

**Trigger**: Time of day (7:00 AM)
**Actions**:
1. Show notification: "Time for coffee?"
2. Wait for user confirmation
3. Run "Log Coffee" shortcut

### Automatic Heart Rate Logging

**Trigger**: After workout ends
**Actions**:
1. Wait 5 minutes
2. Get heart rate from Health
3. Run "Log Heart Rate" shortcut

### Daily Summary

**Trigger**: Time of day (10:00 PM)
**Actions**:
1. Get /coffee/today
2. Get /heartrate/stats
3. Show notification with summary

---

## Getting Help

1. Test basic connectivity with `/health` endpoint
2. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
3. Verify API is running: `docker-compose logs coffee-tracker`
4. Test with curl before creating shortcuts
5. Check API docs: `https://coffee.danilocloud.me/docs`

---

## Resources

- **API Documentation**: https://coffee.danilocloud.me/docs
- **Health Endpoint**: https://coffee.danilocloud.me/health
- **Apple Shortcuts User Guide**: https://support.apple.com/guide/shortcuts/
- **Troubleshooting Guide**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

**Last Updated**: 2024-10-05  
**API Version**: 1.0.0  
**Compatible with**: iOS 13+, iPadOS 13+, macOS 12+

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
