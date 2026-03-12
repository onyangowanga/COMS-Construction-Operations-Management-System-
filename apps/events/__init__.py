"""
COMS Event Logging Module

This module provides comprehensive event logging across the entire COMS platform.
It tracks all significant user actions, system events, and entity changes.

Key Features:
- Automatic event logging via middleware
- Manual event logging via services
- Entity-level event tracking
- Project-level event aggregation
- User activity monitoring
- API action logging
"""

default_app_config = 'apps.events.apps.EventsConfig'
