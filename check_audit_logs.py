#!/usr/bin/env python
"""
Check recent audit logs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import AuditLog

logs = AuditLog.objects.all().order_by('-timestamp')[:10]

print("\n" + "="*100)
print("RECENT AUDIT LOGS")
print("="*100)
print(f"{'Timestamp':<20} | {'Action':<20} | {'User':<25} | {'IP Address':<15} | Details")
print("-"*100)

for log in logs:
    user_email = log.user.email if log.user else 'Anonymous'
    ip_addr = log.ip_address if log.ip_address else 'N/A'
    details = str(log.details)[:30] if log.details else ''
    print(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20} | {log.action:<20} | {user_email:<25} | {ip_addr:<15} | {details}")

print("="*100)
print(f"Total audit logs in database: {AuditLog.objects.count()}")
print()

# Check token blacklist
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

print("\n" + "="*100)
print("TOKEN BLACKLIST STATUS")
print("="*100)
print(f"Outstanding tokens: {OutstandingToken.objects.count()}")
print(f"Blacklisted tokens: {BlacklistedToken.objects.count()}")
print("="*100)
