# Authentication System Documentation

## Overview

Jobsight uses **Django's built-in session-based authentication**, which is the standard and secure approach for web applications. This document explains how authentication works, session management, and why we don't use refresh tokens.

## Current Authentication System

### Session-Based Authentication

Our application uses Django's session framework with the following characteristics:

- **Session Storage**: Sessions are stored in the database (PostgreSQL/Supabase)
- **Session Duration**: 7 days by default (configurable)
- **Session Extension**: Sessions are automatically extended on each request
- **Security**: HTTP-only cookies with CSRF protection

### Configuration

```python
# Session Configuration
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session alive when browser closes
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request
SESSION_COOKIE_SECURE = not DEBUG  # Secure cookies in production
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

## Why No Refresh Tokens?

### What are Refresh Tokens?

Refresh tokens are typically used in:
- **JWT (JSON Web Token) authentication**
- **API-based applications**
- **Mobile apps**
- **Single Page Applications (SPAs)**

### Why We Don't Use Them

1. **Traditional Web Application**: Jobsight is a traditional server-rendered web application, not a SPA
2. **Session-Based is Sufficient**: Django's session framework provides all the security and functionality we need
3. **Simpler Architecture**: No need for complex token management
4. **Better Security**: Sessions are stored server-side and can be invalidated immediately

## Session Management Features

### Automatic Session Extension

Sessions are automatically extended when users interact with the site:

```python
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request
```

### Client-Side Session Monitoring

We've implemented client-side session monitoring that:

1. **Checks Session Status**: Every minute, the frontend checks if the session is still valid
2. **Shows Warnings**: 5 minutes before expiry, users see a warning notification
3. **Allows Extension**: Users can click "Stay Logged In" to extend their session
4. **Automatic Redirect**: If session expires, users are redirected to login

### API Endpoints

```python
# Check session status
GET /api/session-status/

# Extend session
POST /api/extend-session/
```

## Security Features

### Session Security

- **HTTP-Only Cookies**: Prevents XSS attacks from stealing session data
- **Secure Cookies**: In production, cookies are only sent over HTTPS
- **CSRF Protection**: All forms include CSRF tokens
- **SameSite Cookies**: Prevents CSRF attacks

### Session Invalidation

Sessions can be invalidated in several ways:

1. **Manual Logout**: User clicks logout
2. **Session Expiry**: Session reaches its maximum age
3. **Server-Side Invalidation**: Admin can invalidate sessions
4. **Password Change**: Sessions are invalidated when password changes

## User Experience

### Login Flow

1. User enters email/password
2. Django authenticates credentials
3. Session is created and stored in database
4. User is redirected to appropriate page (job list or employer home)

### Session Persistence

- **Browser Close**: Sessions persist when browser is closed
- **Multiple Tabs**: Session works across all browser tabs
- **Automatic Extension**: Sessions extend automatically with use
- **Warning System**: Users get warnings before session expiry

### Logout Flow

1. User clicks logout
2. Session is deleted from database
3. User is redirected to job list page
4. All session data is cleared

## Configuration Options

### Session Duration

You can adjust session duration by modifying `SESSION_COOKIE_AGE`:

```python
# 1 day
SESSION_COOKIE_AGE = 60 * 60 * 24

# 2 weeks
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# 1 month
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
```

### Browser Close Behavior

```python
# Sessions expire when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Sessions persist when browser closes (current setting)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

## Troubleshooting

### Common Issues

1. **Session Expiring Too Quickly**
   - Check `SESSION_COOKIE_AGE` setting
   - Ensure `SESSION_SAVE_EVERY_REQUEST = True`

2. **Sessions Not Persisting**
   - Check `SESSION_EXPIRE_AT_BROWSER_CLOSE` setting
   - Verify database connection for session storage

3. **Security Warnings**
   - Ensure `SESSION_COOKIE_SECURE = True` in production
   - Check `SESSION_COOKIE_HTTPONLY = True`

### Debugging

To debug session issues, you can:

1. **Check Session Data**:
   ```python
   print(request.session.items())
   ```

2. **Check Session Expiry**:
   ```python
   print(request.session.get_expiry_date())
   ```

3. **Force Session Save**:
   ```python
   request.session.modified = True
   ```

## Best Practices

1. **Regular Security Audits**: Review session configuration regularly
2. **Monitor Session Usage**: Track session creation and expiry
3. **Implement Rate Limiting**: Prevent brute force attacks
4. **Use HTTPS**: Always use HTTPS in production
5. **Regular Logout**: Encourage users to logout when done

## Future Considerations

If we ever need to implement refresh tokens (e.g., for a mobile app or API), we would:

1. **Add JWT Support**: Implement JWT authentication alongside sessions
2. **Create API Endpoints**: Add token-based authentication endpoints
3. **Maintain Backward Compatibility**: Keep session-based auth for web interface
4. **Implement Token Refresh**: Add refresh token rotation and validation

## Conclusion

Our session-based authentication system provides:
- ✅ **Security**: Server-side session storage with CSRF protection
- ✅ **Simplicity**: No complex token management
- ✅ **User Experience**: Seamless session extension and warnings
- ✅ **Flexibility**: Easy to configure and customize
- ✅ **Standards Compliance**: Follows Django best practices

This approach is perfect for our web application and provides all the security and functionality we need without unnecessary complexity. 