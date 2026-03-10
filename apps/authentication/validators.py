"""
Authentication Validators
Custom validation functions for user input, files, and business rules.
Keeps validation logic centralized and reusable.
"""
import re
import os
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils.translation import gettext_lazy as _

from .constants import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_REQUIRE_LOWERCASE,
    PASSWORD_REQUIRE_DIGIT,
    PASSWORD_REQUIRE_SPECIAL_CHAR,
    PHONE_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_REGEX_PATTERN,
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX_PATTERN,
    PROFILE_PICTURE_MAX_SIZE_MB,
    PROFILE_PICTURE_ALLOWED_EXTENSIONS,
    ORGANIZATION_LOGO_MAX_SIZE_MB,
    ORGANIZATION_LOGO_ALLOWED_EXTENSIONS,
)


def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone:
        return
    
    # Remove whitespace
    phone = phone.strip()
    
    # Check length
    clean_phone = re.sub(r'[^\d]', '', phone)
    if len(clean_phone) < PHONE_MIN_LENGTH or len(clean_phone) > PHONE_MAX_LENGTH:
        raise ValidationError(
            _(f'Phone number must be between {PHONE_MIN_LENGTH} and {PHONE_MAX_LENGTH} digits.')
        )
    
    # Check format
    if not re.match(PHONE_REGEX_PATTERN, phone):
        raise ValidationError(
            _("Phone number must be in format: '+999999999'. Up to 15 digits allowed.")
        )


def validate_password_strength(password):
    """
    Validate password meets security requirements.
    
    Args:
        password: Password string
        
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    errors = []
    
    # Check length
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f'Password must be at least {PASSWORD_MIN_LENGTH} characters long.')
    
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f'Password must not exceed {PASSWORD_MAX_LENGTH} characters.')
    
    # Check for uppercase
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    
    # Check for lowercase
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')
    
    # Check for digit
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        errors.append('Password must contain at least one digit.')
    
    # Check for special character
    if PASSWORD_REQUIRE_SPECIAL_CHAR and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
    
    # Check for common weak passwords
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    if password.lower() in common_passwords:
        errors.append('This password is too common. Please choose a stronger password.')
    
    if errors:
        raise ValidationError(errors)


def validate_username(username):
    """
    Validate username format.
    
    Args:
        username: Username string
        
    Raises:
        ValidationError: If username is invalid
    """
    if not username:
        raise ValidationError(_('Username is required.'))
    
    # Check length
    if len(username) < USERNAME_MIN_LENGTH:
        raise ValidationError(
            _(f'Username must be at least {USERNAME_MIN_LENGTH} characters long.')
        )
    
    if len(username) > USERNAME_MAX_LENGTH:
        raise ValidationError(
            _(f'Username must not exceed {USERNAME_MAX_LENGTH} characters.')
        )
    
    # Check format (alphanumeric, underscore, hyphen, period)
    if not re.match(USERNAME_REGEX_PATTERN, username):
        raise ValidationError(
            _('Username can only contain letters, numbers, underscores, hyphens, and periods.')
        )
    
    # Check reserved usernames
    reserved_usernames = [
        'admin', 'administrator', 'root', 'system', 'api', 'support',
        'help', 'info', 'contact', 'sales', 'billing', 'security'
    ]
    if username.lower() in reserved_usernames:
        raise ValidationError(_('This username is reserved and cannot be used.'))


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError(_('Email is required.'))
    
    # Use Django's built-in validator
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError(_('Enter a valid email address.'))
    
    # Check for disposable email domains (optional)
    disposable_domains = [
        'tempmail.com', 'throwaway.email', '10minutemail.com',
        'guerrillamail.com', 'mailinator.com'
    ]
    domain = email.split('@')[-1].lower()
    if domain in disposable_domains:
        raise ValidationError(
            _('Disposable email addresses are not allowed. Please use a permanent email address.')
        )


def validate_file_size(file, max_size_mb):
    """
    Validate uploaded file size.
    
    Args:
        file: UploadedFile object
        max_size_mb: Maximum allowed size in megabytes
        
    Raises:
        ValidationError: If file is too large
    """
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _(f'File size must not exceed {max_size_mb} MB. Current size: {file.size / (1024 * 1024):.2f} MB.')
        )


def validate_file_extension(file, allowed_extensions):
    """
    Validate uploaded file extension.
    
    Args:
        file: UploadedFile object
        allowed_extensions: List of allowed extensions (without dots)
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f'File type ".{ext}" is not allowed. Allowed types: {", ".join(allowed_extensions)}.')
        )


def validate_profile_picture(file):
    """
    Validate profile picture upload.
    
    Args:
        file: UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    if file:
        validate_file_size(file, PROFILE_PICTURE_MAX_SIZE_MB)
        validate_file_extension(file, PROFILE_PICTURE_ALLOWED_EXTENSIONS)


def validate_organization_logo(file):
    """
    Validate organization logo upload.
    
    Args:
        file: UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    if file:
        validate_file_size(file, ORGANIZATION_LOGO_MAX_SIZE_MB)
        validate_file_extension(file, ORGANIZATION_LOGO_ALLOWED_EXTENSIONS)


def validate_tax_id(tax_id, country='US'):
    """
    Validate tax identification number format.
    
    Args:
        tax_id: Tax ID string
        country: Country code (for country-specific validation)
        
    Raises:
        ValidationError: If tax ID is invalid
    """
    if not tax_id:
        return
    
    tax_id = tax_id.strip().replace('-', '').replace(' ', '')
    
    if country == 'US':
        # US EIN format: XX-XXXXXXX (9 digits)
        if not re.match(r'^\d{9}$', tax_id):
            raise ValidationError(
                _('US Tax ID (EIN) must be 9 digits in format: XX-XXXXXXX.')
            )
    elif country == 'UK':
        # UK VAT format: GB followed by 9 or 12 digits
        if not re.match(r'^(GB)?\d{9}(\d{3})?$', tax_id):
            raise ValidationError(
                _('UK VAT number must be 9 or 12 digits, optionally prefixed with GB.')
            )
    # Add more country-specific validations as needed


def validate_registration_number(reg_number):
    """
    Validate business registration number.
    
    Args:
        reg_number: Registration number string
        
    Raises:
        ValidationError: If registration number is invalid
    """
    if not reg_number:
        return
    
    reg_number = reg_number.strip()
    
    # Basic validation - alphanumeric with common separators
    if not re.match(r'^[A-Z0-9\-/]+$', reg_number.upper()):
        raise ValidationError(
            _('Registration number can only contain letters, numbers, hyphens, and slashes.')
        )
    
    if len(reg_number) < 3 or len(reg_number) > 50:
        raise ValidationError(
            _('Registration number must be between 3 and 50 characters.')
        )


def validate_job_title(job_title):
    """
    Validate job title.
    
    Args:
        job_title: Job title string
        
    Raises:
        ValidationError: If job title is invalid
    """
    if not job_title:
        return
    
    if len(job_title) < 2:
        raise ValidationError(_('Job title must be at least 2 characters long.'))
    
    if len(job_title) > 100:
        raise ValidationError(_('Job title must not exceed 100 characters.'))
    
    # Allow letters, spaces, hyphens, apostrophes, periods
    if not re.match(r"^[a-zA-Z\s\-'.]+$", job_title):
        raise ValidationError(
            _('Job title can only contain letters, spaces, hyphens, apostrophes, and periods.')
        )


def validate_organization_name(name):
    """
    Validate organization/company name.
    
    Args:
        name: Organization name string
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError(_('Organization name is required.'))
    
    if len(name) < 2:
        raise ValidationError(_('Organization name must be at least 2 characters long.'))
    
    if len(name) > 255:
        raise ValidationError(_('Organization name must not exceed 255 characters.'))
    
    # Basic sanitization - no leading/trailing special characters
    if re.match(r'^[^a-zA-Z0-9]|[^a-zA-Z0-9]$', name):
        raise ValidationError(
            _('Organization name must start and end with a letter or number.')
        )


def validate_ip_address(ip_address):
    """
    Validate IP address (IPv4 or IPv6).
    
    Args:
        ip_address: IP address string
        
    Raises:
        ValidationError: If IP address is invalid
    """
    import ipaddress
    
    if not ip_address:
        return
    
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise ValidationError(_('Enter a valid IPv4 or IPv6 address.'))


def validate_notes_length(notes, max_length=1000):
    """
    Validate notes/comments field length.
    
    Args:
        notes: Notes string
        max_length: Maximum allowed length
        
    Raises:
        ValidationError: If notes exceed max length
    """
    if notes and len(notes) > max_length:
        raise ValidationError(
            _(f'Notes must not exceed {max_length} characters. Current length: {len(notes)}.')
        )
