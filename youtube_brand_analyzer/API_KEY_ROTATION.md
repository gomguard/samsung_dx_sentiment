# YouTube API Key Rotation System

## Overview

YouTube Data API v3 has a daily quota limit of 10,000 units per API key. To extend collection capacity, the system now supports **automatic API key rotation** with multiple keys.

## How It Works

### 1. Configuration
Multiple API keys are configured in `config/secrets.py`:

```python
YOUTUBE_API_KEYS = [
    "AIzaSyBSaxM4BClWmPW6ZM2EKaI1qcAROsCUUYQ",  # Account 1
    "AIzaSyDhxXIESSjnCcTGiZoa63Z3AfgqAbxlZv4",  # Account 2
    "AIzaSyDNMhNDsZK1D-1Xu7dNk_0Gr6svrw3MNnE",  # Account 3
]
```

### 2. Automatic Detection
When any API call returns a quota exceeded error, the system:
- Detects the error automatically
- Logs the quota exceeded event
- Switches to the next available API key
- Retries the failed request immediately

### 3. Key Rotation Process

```
API Call → Quota Exceeded Error
    ↓
Detect "quotaExceeded" in error
    ↓
Rotate to next key (if available)
    ↓
Rebuild YouTube client with new key
    ↓
Retry the same API call
    ↓
Success (or repeat if still quota exceeded)
```

### 4. Capacity Extension

With 3 API keys, total daily capacity:
- **Single key**: ~10,000 units/day
- **3 keys**: ~30,000 units/day (3x capacity)

Estimated collection capacity per day:
- Video search: ~300-500 videos per key
- With 3 keys: **~900-1,500 videos/day**

## Usage

### Default Usage (Automatic)

```python
from collectors.youtube_api import YouTubeAnalyzer

# Automatically loads all keys from YOUTUBE_API_KEYS
analyzer = YouTubeAnalyzer()

# Key rotation happens automatically on quota exceeded
video_data, video_ids, raw_data = analyzer.get_comprehensive_video_data(
    keyword="Samsung TV",
    max_results=100
)
```

### Custom Keys

```python
# Use specific keys
custom_keys = ["key1", "key2", "key3"]
analyzer = YouTubeAnalyzer(api_keys=custom_keys)
```

## Monitoring

### Console Output

When rotation occurs, you'll see:

```
[QUOTA EXCEEDED] API 할당량 초과 감지
[KEY ROTATION] API 키 #2로 전환됨 (잔여 키: 1개)
[RETRY] 새 API 키로 재시도...
```

### Check Current Key

```python
print(f"Current key index: {analyzer.current_key_index}")
print(f"Total keys: {len(analyzer.api_keys)}")
print(f"Remaining keys: {len(analyzer.api_keys) - analyzer.current_key_index - 1}")
```

## Error Handling

### All Keys Exhausted

If all API keys reach quota limit:

```
[ERROR] 모든 API 키의 할당량이 소진되었습니다 (3개 키 모두 사용)
Exception: 모든 API 키의 할당량이 소진되었습니다
```

### Other Errors

Non-quota errors are retried up to 3 times before failing:

```
[API ERROR] 에러 발생, 재시도 중... (1/3)
```

## API Quota Usage

### Typical Usage per Operation

- **Video Search** (search.list): 100 units
- **Video Details** (videos.list): 1 unit
- **Channel Info** (channels.list): 1 unit
- **Comments** (commentThreads.list): 1 unit

### Example: Collecting 100 videos

1. Search: 4 pages × 100 units = 400 units
2. Video details: 100 × 1 unit = 100 units
3. Channel info: ~50 channels × 1 unit = 50 units
4. Comments: 100 videos × 1 unit = 100 units

**Total**: ~650 units for 100 videos with comments

### Daily Capacity Estimate

- Single key (10,000 units): ~1,500 videos
- 3 keys (30,000 units): **~4,500 videos/day**

## Best Practices

1. **Monitor Usage**: Check console output for key rotation events
2. **Spread Collection**: Distribute large collections across multiple days if needed
3. **Add More Keys**: Create more YouTube Data API projects for additional capacity
4. **Rate Limiting**: System includes built-in delays to avoid rate limits

## Adding More API Keys

### Step 1: Create New Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create new project
3. Enable YouTube Data API v3
4. Create API credentials (API key)

### Step 2: Add to Configuration
Edit `config/secrets.py`:

```python
YOUTUBE_API_KEYS = [
    "key1",
    "key2",
    "key3",
    "key4",  # New key
]
```

### Step 3: Restart Application
The new key will be automatically loaded on next run.

## Implementation Details

### Modified Files

1. **config/secrets.py**: Multiple API keys configuration
2. **config/settings.py**: Import YOUTUBE_API_KEYS
3. **youtube_api.py**: Key rotation logic
   - `__init__()`: Load multiple keys
   - `_rotate_api_key()`: Switch to next key
   - `_execute_with_retry()`: Wrapper for API calls with retry

### Protected API Calls

All YouTube API calls are wrapped with `_execute_with_retry()`:
- `search().list()` - Video search
- `videos().list()` - Video details
- `channels().list()` - Channel info
- `commentThreads().list()` - Comments

## Testing

Run the test script to verify key rotation:

```bash
cd youtube_brand_analyzer
python test_key_rotation.py
```

Expected output:
```
YouTubeAnalyzer 초기화: 3개 API 키 사용 가능
[QUOTA EXCEEDED] API 할당량 초과 감지
[KEY ROTATION] API 키 #2로 전환됨 (잔여 키: 1개)
[OK] API call successful!
```

## Quota Reset

- YouTube API quotas reset daily at **midnight Pacific Time (PST/PDT)**
- All keys reset simultaneously
- Plan large collections to start after quota reset

## Troubleshooting

### Issue: Keys rotate but still fail
**Solution**: All keys may have reached quota. Wait for daily reset.

### Issue: "Invalid API key" error
**Solution**: Check that all keys in YOUTUBE_API_KEYS are valid and have YouTube Data API v3 enabled.

### Issue: Rotation doesn't work
**Solution**:
1. Verify `YOUTUBE_API_KEYS` is a list in secrets.py
2. Check that settings.py imports YOUTUBE_API_KEYS
3. Restart the application

## Summary

The API key rotation system provides:
- ✅ **3x capacity** with 3 keys
- ✅ **Automatic failover** on quota exceeded
- ✅ **Seamless operation** - no manual intervention
- ✅ **Easy expansion** - just add more keys
- ✅ **Robust error handling** - retries and logging

This allows continuous data collection even with API quota limits!
