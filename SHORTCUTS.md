# Apple Shortcuts Integration Guide

This guide shows you how to log coffee and heart rate data from your iPhone using Apple Shortcuts.

## Prerequisites

- iPhone with Shortcuts app installed
- API deployed at `https://coffee.danilocloud.me`
- Your API key from `.env` file: `coffee-addict-secret-key-2025`

## Quick Setup

### 1. Log Coffee Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create new shortcut
3. Add the following actions:

```
Action 1: Ask for Input
  - Prompt: "How much caffeine? (mg)"
  - Type: Number
  - Default: 120

Action 2: Ask for Input
  - Prompt: "Coffee type?"
  - Type: Text
  - Default: "Americano"

Action 3: Ask for Input
  - Prompt: "Notes (optional)"
  - Type: Text
  - (Optional)

Action 4: Get Contents of URL
  - URL: https://coffee.danilocloud.me/coffee/
  - Method: POST
  - Headers:
      Authorization: Bearer coffee-addict-secret-key-2025
      Content-Type: application/json
  - Request Body: JSON
      {
        "caffeine_mg": [Provided Input from Action 1],
        "coffee_type": "[Provided Input from Action 2]",
        "notes": "[Provided Input from Action 3]"
      }

Action 5: Show Notification
  - Title: "Coffee Logged ☕"
  - Body: "[Contents of URL]"
```

4. Name the shortcut **"Log Coffee"**
5. Add to Home Screen or use with Siri: *"Hey Siri, log coffee"*

### 2. Log Heart Rate Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create new shortcut
3. Add the following actions:

```
Action 1: Get Current Heart Rate
  (This reads from Apple Health/Watch)

Action 2: Ask for Input
  - Prompt: "Context?"
  - Type: Text
  - Default: "resting"
  - Suggested: "resting", "post-coffee", "exercise", "stressed"

Action 3: Ask for Input
  - Prompt: "Notes (optional)"
  - Type: Text
  - (Optional)

Action 4: Get Contents of URL
  - URL: https://coffee.danilocloud.me/heartrate/
  - Method: POST
  - Headers:
      Authorization: Bearer coffee-addict-secret-key-2025
      Content-Type: application/json
  - Request Body: JSON
      {
        "bpm": [Heart Rate],
        "context": "[Provided Input from Action 2]",
        "notes": "[Provided Input from Action 3]"
      }

Action 5: Show Notification
  - Title: "Heart Rate Logged ❤️"
  - Body: "[Contents of URL]"
```

4. Name the shortcut **"Log Heart Rate"**
5. Add to Home Screen or use with Siri: *"Hey Siri, log heart rate"*

### 3. Quick Coffee Presets

Create faster shortcuts for common coffee types:

**Quick Espresso** (95mg):
```
Action 1: Get Contents of URL
  - URL: https://coffee.danilocloud.me/coffee/
  - Method: POST
  - Headers: Authorization: Bearer coffee-addict-secret-key-2025
  - Body: {"caffeine_mg": 95, "coffee_type": "espresso"}
```

**Quick Americano** (120mg):
```
Same as above but with:
  - Body: {"caffeine_mg": 120, "coffee_type": "americano"}
```

**Quick Latte** (150mg):
```
Same as above but with:
  - Body: {"caffeine_mg": 150, "coffee_type": "latte"}
```

## Advanced: Automation

### Auto-log Heart Rate After Coffee

1. Create new **Automation** (not shortcut)
2. Trigger: **When I run a shortcut** → Select "Log Coffee"
3. Action: **Wait 15 minutes**
4. Action: **Run Shortcut** → Select "Log Heart Rate"

This automatically checks your heart rate 15 minutes after logging coffee!

### Morning Coffee Reminder

1. Create new **Automation**
2. Trigger: **Time of Day** → 8:00 AM
3. Action: **Show Notification** → "Time for morning coffee ☕"
4. Action: **Run Shortcut** → "Log Coffee"

## API Endpoints

- **Log Coffee**: `POST https://coffee.danilocloud.me/coffee/`
- **Log Heart Rate**: `POST https://coffee.danilocloud.me/heartrate/`
- **View Today**: `GET https://coffee.danilocloud.me/coffee/today`
- **View Stats**: `GET https://coffee.danilocloud.me/coffee/stats`
- **Health Check**: `GET https://coffee.danilocloud.me/health`

## Request Format

### Coffee Request Body
```json
{
  "caffeine_mg": 120,        // Required: 0-1000
  "coffee_type": "americano", // Optional: max 100 chars
  "notes": "Feeling great!"   // Optional: max 1000 chars
}
```

### Heart Rate Request Body
```json
{
  "bpm": 75,                  // Required: 30-250
  "context": "resting",       // Optional: max 50 chars
  "notes": "Morning reading"  // Optional: max 1000 chars
}
```

## Troubleshooting

### "Could not connect to server"
- Check your internet connection
- Verify the URL is correct: `https://coffee.danilocloud.me`

### "401 Unauthorized"
- Verify your API key is correct in the Authorization header
- Format: `Bearer coffee-addict-secret-key-2025`

### "422 Validation Error"
- Check caffeine_mg is between 0-1000
- Check bpm is between 30-250
- Verify JSON format is correct

### "Can't read heart rate"
- Grant Shortcuts access to Health data in Settings → Privacy → Health
- Make sure Apple Watch is connected and synced

## Privacy & Security

- **API Key**: Keep your API key secure. Don't share shortcuts that contain it publicly.
- **Health Data**: Shortcuts will ask for permission to read heart rate data
- **Data Storage**: All data is stored securely in your PostgreSQL database
- **HTTPS**: All communication is encrypted via HTTPS

## Tips

1. **Home Screen Widgets**: Add shortcuts to home screen for one-tap logging
2. **Siri**: Use voice commands: "Hey Siri, log coffee"
3. **Share Sheet**: Add shortcuts to share sheet for quick access
4. **Watch Complications**: Add to Apple Watch face for instant access
5. **NFC Tags**: Create NFC tags near your coffee machine to auto-trigger logging

## Example Use Cases

1. **Morning Routine**: Auto-log espresso at 7 AM
2. **Pre-workout**: Log caffeine + heart rate before exercise
3. **Work Session**: Track caffeine during focus periods
4. **Sleep Analysis**: Correlate late caffeine with sleep quality
5. **Health Monitoring**: Track heart rate response to caffeine over time

## Next Steps

- View analytics at `/docs` endpoint
- Check today's stats with `/coffee/today`
- Monitor heart rate correlation with `/heartrate/correlation`
- Set up Grafana dashboards for visualization

For more details, see the API documentation at `https://coffee.danilocloud.me/docs`
