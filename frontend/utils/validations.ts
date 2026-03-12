// ============================================================================
// VALIDATION SCHEMAS
// Zod schemas for form validation
// ============================================================================

import { z } from 'zod';

// ============================================================================
// Auth Schemas
// ============================================================================

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine(data => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

// ============================================================================
// Project Schemas
// ============================================================================

export const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required'),
  code: z.string().min(1, 'Project code is required'),
  description: z.string().optional(),
  client: z.string().min(1, 'Client is required'),
  status: z.enum(['planning', 'active', 'on_hold', 'completed', 'cancelled']),
  type: z.enum(['building', 'infrastructure', 'renovation', 'civil_works']),
  contract_value: z.string().min(1, 'Contract value is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  location: z.string().optional(),
  project_manager: z.string().optional(),
});

// ============================================================================
// Variation Schemas
// ============================================================================

export const variationSchema = z.object({
  project: z.string().min(1, 'Project is required'),
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  estimated_value: z.string().min(1, 'Estimated value is required'),
});

// ============================================================================
// Claim Schemas
// ============================================================================

export const claimSchema = z.object({
  project: z.string().min(1, 'Project is required'),
  title: z.string().min(1, 'Title is required'),
  claim_period_start: z.string().min(1, 'Period start date is required'),
  claim_period_end: z.string().min(1, 'Period end date is required'),
  gross_amount: z.string().min(1, 'Gross amount is required'),
  retention: z.string().optional(),
});

// ============================================================================
// Document Schemas
// ============================================================================

export const documentSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  category: z.string().min(1, 'Category is required'),
  project: z.string().optional(),
  file: z.any(),
});
