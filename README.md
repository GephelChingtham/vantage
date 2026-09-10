# Vantage

Communication auditor for analyzing effort asymmetry and intent.

## Quick Start

```bash
git clone https://github.com/GephelChingtham/vantage.git
cd vantage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## Test

```bash
curl http://localhost:8000/health
```

## Upload Chat

```bash
cat > test.txt << 'EOT'
[8/15/24, 2:34 PM] Alice: Hey, can we talk?
[8/15/24, 4:20 PM] Bob: Maybe, later
[8/15/24, 4:25 PM] Alice: When are you free?
[8/16/24, 10:00 AM] Bob: Eventually
EOT

curl -X POST -F "file=@test.txt" http://localhost:8000/api/v1/analyze
```

## API

- `GET /health` - Health check
- `POST /api/v1/analyze` - Upload chat
- `GET /api/v1/job/{job_id}` - Get results
- `DELETE /api/v1/user/{user_id}` - GDPR delete

## Privacy

Raw chat deleted after 7 days. No data stored long-term.
