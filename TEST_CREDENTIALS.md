# Test Credentials

## Regular User Account

- **Email:** user@demo.com
- **Password:** UserPass123!
- **Access:** Dashboard and general features

## Admin Account

- **Email:** admin@example.com
- **Password:** AdminPass123!
- **Access:** Admin Panel at `/admin` with stats and analytics

## Using These Credentials

### Frontend Login

1. Go to http://localhost:5173
2. Click "Sign In"
3. Enter email and password
4. Click login

### Backend API Test

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@demo.com","password":"UserPass123!"}'
```

## Database Location

- **SQLite Database:** `backend/learning_platform.db`
- **User Records:** Stored with pbkdf2_sha256 hashed passwords

## Notes

- Both accounts are active and ready to use
- Passwords are hashed in the database (pbkdf2_sha256)
- JWT tokens expire after 1440 minutes (24 hours)
- Admin account has access to `/admin/stats` endpoint
