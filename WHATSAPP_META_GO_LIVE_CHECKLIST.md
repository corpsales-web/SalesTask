# Meta WhatsApp Cloud API – Go-Live Checklist (Aavana Greens CRM)

This app currently runs in STUB mode when Meta credentials are not present. Use this checklist to switch to LIVE mode safely.

## 1) Required Credentials (obtain from Meta for Developers)
- WHATSAPP_ACCESS_TOKEN (Permanent, system user token)
- WHATSAPP_PHONE_NUMBER_ID (from WhatsApp Manager)
- WHATSAPP_BUSINESS_ACCOUNT_ID (WABA ID)
- WHATSAPP_APP_SECRET (App secret for webhook signature validation)
- WHATSAPP_VERIFY_TOKEN (Choose your own string for webhook verification)
- WHATSAPP_API_VERSION (optional, default v20.0)

Where to get them:
- https://developers.facebook.com/apps → Your App → WhatsApp → Getting Started
- Phone Number ID & WABA ID from WhatsApp Manager
- Generate a System User Token under Business Settings → System Users

## 2) Configure environment (backend)
Add secrets to backend environment (.env already loaded by FastAPI):
- WHATSAPP_ACCESS_TOKEN=...
- WHATSAPP_PHONE_NUMBER_ID=...
- WHATSAPP_BUSINESS_ACCOUNT_ID=...
- WHATSAPP_APP_SECRET=...
- WHATSAPP_VERIFY_TOKEN=...
- WHATSAPP_API_VERSION=v20.0

Restart backend via supervisor:
- sudo supervisorctl restart backend

Live mode is automatically enabled when ACCESS_TOKEN and PHONE_NUMBER_ID are present.

## 3) Webhook setup
- Public URL: Use the same external URL used by the frontend (ingress) and append /api/whatsapp/webhook
- Verify Token: Use WHATSAPP_VERIFY_TOKEN value
- Subscription fields: messages
- After saving, send a test message from a WhatsApp number to your connected phone number

## 4) Allowlist callback domains (if required)
- Ensure your domain is added in App settings → WhatsApp configuration

## 5) Dry-run tests (no UI change)
Backend
- GET /api/health → {status: ok}
- GET /api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=1234 → returns 1234
- POST /api/whatsapp/webhook with a sample payload signed with APP_SECRET → 200 {success:true}

Outbound send
- POST /api/whatsapp/send {to, text} → 200 with {provider: meta} (not stub)
- POST /api/whatsapp/send_media {to, media_url, media_type} → 200 with {success:true}
- POST /api/whatsapp/send_template {to, template_name, language_code} → 200 with {provider: meta}

Inbox
- GET /api/whatsapp/conversations → should show inbound contact with last_message_text
- GET /api/whatsapp/contact_messages?contact=+91XXXXXXXXXX → recent messages

## 6) Error handling & common issues
- 401 Provider error: Check ACCESS_TOKEN validity and business app permissions
- 400 Invalid recipient: Ensure number is in international format (+91...) and opted in
- 403 Permission denied: Verify app is in Live mode and WhatsApp Business permissions/phone number ownership
- 401 Invalid signature on webhook: Confirm WHATSAPP_APP_SECRET matches app’s secret and header X-Hub-Signature-256 provided

## 7) Production readiness
- Rotate & securely store tokens
- Monitor /api/whatsapp/webhook errors
- Set up retry policies and dead-letter queue (future enhancement)

Notes
- No hardcoded URLs. All backend routes are prefixed with /api and respect ingress rules.
- Switching from stub → live is automatic based on presence of env vars.
