// ============================================================================
// LOGIN PAGE
// User authentication page
// ============================================================================

'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { LogIn, Eye, EyeOff } from 'lucide-react';
import { useAuth, useToast } from '@/hooks';
import { Button, Input, Card } from '@/components/ui';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuth();
  const { error: showError } = useToast();

  const [showPassword, setShowPassword] = useState(false);
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!credentials.email || !credentials.password) {
      showError('Validation Error', 'Please enter both email and password');
      return;
    }

    try {
      await login(credentials);
      // Redirect handled by login function
    } catch (error: any) {
      showError('Login Failed', error.message || 'Invalid credentials');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-secondary-700 px-4">
        <Card className="w-full max-w-md" padding="lg">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              {/* Using a fixed-size wrapper with 'relative' and 'fill'
              ensures the logo size stays consistent across all environments.
            */}
              <div className="relative w-20 h-20">
                <Image
                    src="/logo_edited.png"
                    alt="COMS Logo"
                    fill
                    sizes="80px"
                    className="rounded-lg shadow-lg object-contain"
                    priority
                />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">COMS</h1>
            <p className="text-gray-600">Construction Operations Management System</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
                label="Email"
                type="email"
                name="email"
                autoComplete="email"
                value={credentials.email}
                onChange={(e) =>
                    setCredentials({ ...credentials, email: e.target.value })
                }
                required
                disabled={isLoading}
                autoFocus
            />

            <div className="relative">
              <Input
                  label="Password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={credentials.password}
                  onChange={(e) =>
                      setCredentials({ ...credentials, password: e.target.value })
                  }
                  required
                  disabled={isLoading}
              />
              <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                ) : (
                    <Eye className="h-5 w-5" />
                )}
              </button>
            </div>

            <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
                leftIcon={<LogIn className="h-5 w-5" />}
            >
              Sign In
            </Button>

            <div className="text-center text-sm text-gray-600">
              <a
                  href="/forgot-password"
                  className="text-primary-600 hover:text-primary-700 hover:underline"
              >
                Forgot password?
              </a>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
            <p>&copy; 2026 COMS. All rights reserved.</p>
          </div>
        </Card>
      </div>
  );
}