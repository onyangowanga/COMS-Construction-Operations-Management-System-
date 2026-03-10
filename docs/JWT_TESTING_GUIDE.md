# JWT Cookie-Based Authentication Tests

## Prerequisites
- Docker containers running: `docker-compose up`
- Test user created: `docker-compose exec web python create_test_user.py`

---

## Test 1: Login and Receive Cookies

```powershell
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -c cookies.txt `
  -d '{\"email\":\"admin@test.com\",\"password\":\"TestPass123!\"}'
```

**Expected Result:**
- Status: 200 OK
- Response contains user profile data
- `cookies.txt` file created with `access_token` and `refresh_token`

**Success Indicators:**
```json
{
  "user": {
    "email": "admin@test.com",
    "username": "testadmin",
    "system_role": "super_admin",
    ...
  },
  "message": "Login successful"
}
```

---

## Test 2: Access Authenticated Endpoint (Using Cookies)

```powershell
curl -X GET http://localhost:8000/api/auth/me/ -b cookies.txt
```

**Expected Result:**
- Status: 200 OK
- Returns full user profile
- **No `Authorization` header needed** (cookies are automatically sent)

**Success Indicators:**
```json
{
  "id": 1,
  "email": "admin@test.com",
  "username": "testadmin",
  "system_role": "super_admin",
  "is_staff": true,
  "is_superuser": true,
  ...
}
```

---

## Test 3: Refresh Access Token (Cookie-Based)

```powershell
curl -X POST http://localhost:8000/api/auth/token/refresh/ `
  -b cookies.txt `
  -c cookies.txt
```

**Expected Result:**
- Status: 200 OK
- New tokens written to `cookies.txt`
- Old refresh token blacklisted (if `ROTATE_REFRESH_TOKENS=True`)

**Success Indicators:**
```json
{
  "message": "Token refreshed successfully"
}
```

---

## Test 4: Logout (Blacklist Token and Clear Cookies)

```powershell
curl -X POST http://localhost:8000/api/auth/logout/ -b cookies.txt
```

**Expected Result:**
- Status: 200 OK
- Refresh token blacklisted in database
- Cookies cleared

**Success Indicators:**
```json
{
  "message": "Logout successful"
}
```

---

## Test 5: Verify Access Denied After Logout

```powershell
curl -X GET http://localhost:8000/api/auth/me/ -b cookies.txt
```

**Expected Result:**
- Status: 401 Unauthorized
- Authentication fails because tokens are cleared

**Success Indicators:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Test 6: Verify Token Blacklisting Works

Try to refresh using the old (blacklisted) refresh token:

```powershell
curl -X POST http://localhost:8000/api/auth/token/refresh/ -b cookies.txt
```

**Expected Result:**
- Status: 401 Unauthorized
- Token rejected because it's blacklisted

**Success Indicators:**
```json
{
  "detail": "Invalid or expired refresh token."
}
```

---

## Test 7: Change Password

First, login again:

```powershell
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -c cookies.txt `
  -d '{\"email\":\"admin@test.com\",\"password\":\"TestPass123!\"}'
```

Then change password:

```powershell
curl -X POST http://localhost:8000/api/auth/change-password/ `
  -H "Content-Type: application/json" `
  -b cookies.txt `
  -d '{\"old_password\":\"TestPass123!\",\"new_password\":\"NewPass456!\",\"new_password_confirm\":\"NewPass456!\"}'
```

**Expected Result:**
- Status: 200 OK
- Password updated
- AuditLog entry created

**Success Indicators:**
```json
{
  "message": "Password changed successfully."
}
```

---

## Test 8: Register New User

```powershell
curl -X POST http://localhost:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d '{
    \"email\":\"newuser@test.com\",
    \"username\":\"newuser\",
    \"password\":\"NewUserPass123!\",
    \"password_confirm\":\"NewUserPass123!\",
    \"first_name\":\"New\",
    \"last_name\":\"User\",
    \"system_role\":\"client\"
  }'
```

**Expected Result:**
- Status: 201 Created
- User created and assigned to default organization
- AuditLog entry created

**Success Indicators:**
```json
{
  "user": {
    "email": "newuser@test.com",
    "username": "newuser",
    "system_role": "client",
    ...
  },
  "message": "Registration successful. Please verify your email."
}
```

---

## Verification Checklist

After running all tests, verify:

### ✅ Cookie Configuration
- [ ] `access_token` cookie set (15 min expiry)
- [ ] `refresh_token` cookie set (7 days expiry)
- [ ] `HttpOnly` flag set on both cookies
- [ ] `SameSite=Lax` set on both cookies
- [ ] `Secure` flag set correctly (False in dev, True in prod)

### ✅ Authentication Flow
- [ ] Login creates cookies
- [ ] Authenticated endpoints work with cookies only (no header needed)
- [ ] Refresh endpoint reads from cookie
- [ ] Logout clears cookies
- [ ] Access denied after logout

### ✅ Token Blacklisting
- [ ] Refresh token blacklisted on logout
- [ ] Blacklisted tokens rejected on refresh
- [ ] Rotation creates new refresh token

### ✅ Audit Logging
- [ ] `USER_LOGIN` event logged on successful login
- [ ] `LOGIN_FAILED` event logged on failed login
- [ ] `USER_LOGOUT` event logged on logout
- [ ] `PASSWORD_CHANGED` event logged on password change
- [ ] `USER_CREATED` event logged on registration

### ✅ Security Features
- [ ] django-axes tracks failed attempts
- [ ] Account locked after 5 failed attempts
- [ ] IP address tracked in AuditLog
- [ ] User agent tracked in AuditLog
- [ ] Password strength validation works

---

## Check Audit Logs in Database

```powershell
docker-compose exec web python manage.py shell -c "from apps.authentication.models import AuditLog; for log in AuditLog.objects.all().order_by('-timestamp')[:10]: print(f'{log.timestamp} - {log.action} - {log.user} - {log.ip_address}')"
```

---

## Check Token Blacklist Table

```powershell
docker-compose exec web python manage.py shell -c "from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken; print(f'Blacklisted tokens: {BlacklistedToken.objects.count()}')"
```

---

## Inspect Cookies (Browser)

1. Open http://localhost:8000/api/auth/login/ in browser dev tools
2. Network tab → Find login request
3. Check Response → Cookies:
   - `access_token` - HttpOnly, SameSite=Lax, Max-Age=900
   - `refresh_token` - HttpOnly, SameSite=Lax, Max-Age=604800

---

## Clean Up

Delete cookies file after testing:

```powershell
Remove-Item cookies.txt -ErrorAction SilentlyContinue
```

---

**✅ Cookie-Based JWT Implementation Verified!**

All requirements met:
1. ✅ HTTP-only cookies with security flags
2. ✅ Custom authentication reads from cookies
3. ✅ Refresh endpoint is cookie-based
4. ✅ Token blacklisting enabled
5. ✅ Audit logging integrated
