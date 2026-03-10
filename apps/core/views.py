"""
Core Views
Template rendering for authentication and dashboard pages
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import JsonResponse

from apps.authentication.models import User, AuditLog


# Authentication Template Views
@require_http_methods(["GET"])
def login_page(request):
    """Render login page"""
    # Redirect to dashboard if already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'authentication/login.html')


@require_http_methods(["GET"])
def register_page(request):
    """Render registration page"""
    # Redirect to dashboard if already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'authentication/register.html')


@require_http_methods(["POST"])
@login_required
def logout_view(request):
    """
    Handle logout - calls API endpoint to blacklist token.
    This is a wrapper that redirects after logout.
    """
    # The actual logout is handled by the API endpoint via HTMX
    # This view just ensures the redirect happens
    return redirect('login')


# Dashboard Views
@login_required
@require_http_methods(["GET"])
def dashboard_view(request):
    """
    Main dashboard view - role-based content
    """
    user = request.user
    
    # Get current date
    current_date = timezone.now()
    
    # Placeholder statistics (will be replaced with real data)
    stats = {
        'active_projects': 0,
        'team_members': 0,
        'pending_tasks': 0,
        'total_budget': 0,
    }
    
    # Get real team member count if user has organization
    if user.organization:
        stats['team_members'] = User.objects.filter(
            organization=user.organization,
            is_active=True
        ).count()
    
    # Placeholder data for projects (will be replaced with real project model)
    projects = []
    
    # Get recent activity from audit logs
    if user.system_role == 'super_admin':
        # Super admin sees all activity
        recent_activities = AuditLog.objects.all()[:10]
    else:
        # Regular users see their own activity
        recent_activities = AuditLog.objects.filter(user=user)[:10]
    
    # Format activities for template
    activities = []
    for log in recent_activities:
        activity = {
            'description': format_activity_description(log),
            'timestamp': log.timestamp,
            'type_color': get_activity_color(log.action),
            'icon': get_activity_icon(log.action),
        }
        activities.append(activity)
    
    context = {
        'current_date': current_date,
        'stats': stats,
        'projects': projects,
        'activities': activities,
    }
    
    return render(request, 'dashboard/index.html', context)


def format_activity_description(log):
    """Format audit log entry for display"""
    action_descriptions = {
        'user_login': f'{log.user.get_full_name() if log.user else "User"} logged in',
        'user_logout': f'{log.user.get_full_name() if log.user else "User"} logged out',
        'login_failed': 'Failed login attempt',
        'user_created': f'New user account created: {log.user.email if log.user else "Unknown"}',
        'user_updated': f'{log.user.get_full_name() if log.user else "User"} updated their profile',
        'password_changed': f'{log.user.get_full_name() if log.user else "User"} changed their password',
        'password_reset': 'Password reset requested',
        'access_granted': 'Project access granted',
        'access_revoked': 'Project access revoked',
        'permission_changed': 'Permissions updated',
    }
    
    return action_descriptions.get(log.action, f'Action: {log.get_action_display()}')


def get_activity_color(action):
    """Get Bootstrap color class for activity type"""
    color_map = {
        'user_login': 'success',
        'user_logout': 'secondary',
        'login_failed': 'danger',
        'user_created': 'primary',
        'user_updated': 'info',
        'password_changed': 'warning',
        'password_reset': 'warning',
        'access_granted': 'success',
        'access_revoked': 'danger',
        'permission_changed': 'info',
    }
    return color_map.get(action, 'secondary')


def get_activity_icon(action):
    """Get Bootstrap icon for activity type"""
    icon_map = {
        'user_login': 'box-arrow-in-right',
        'user_logout': 'box-arrow-right',
        'login_failed': 'exclamation-triangle',
        'user_created': 'person-plus',
        'user_updated': 'person-check',
        'password_changed': 'key',
        'password_reset': 'shield-lock',
        'access_granted': 'unlock',
        'access_revoked': 'lock',
        'permission_changed': 'shield-check',
    }
    return icon_map.get(action, 'circle')


# Home/Landing Page
@require_http_methods(["GET"])
def home_view(request):
    """
    Home page - redirect to dashboard if authenticated, otherwise login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# API Health Check
@require_http_methods(["GET"])
def health_check(request):
    """API health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'service': 'COMS API'
    })

