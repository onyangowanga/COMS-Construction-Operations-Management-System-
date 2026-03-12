// ============================================================================
// LOGIN PAGE
// User authentication page
// ============================================================================

'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { LogIn } from 'lucide-react';
import { useAuth, useToast } from '@/hooks';
import { Button, Input, Card } from '@/components/ui';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuth();
  const { error: showError } = useToast();
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-secondary-700 px-4">
      <Card className="w-full max-w-md" padding="lg">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Image 
              src="/logo.png" 
              alt="COMS Logo" 
              width={80} 
              height={80}
              className="rounded-lg shadow-lg"
            />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">COMS</h1>
          <p className="text-gray-600">Construction Management System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Email"
            type="email"
            value={credentials.email}
            onChange={(e) =>
              setCredentials({ ...credentials, email: e.target.value })
            }
            required
            disabled={isLoading}
            autoFocus
          />

          <Input
            label="Password"
            type="password"
            value={credentials.password}
            onChange={(e) =>
              setCredentials({ ...credentials, password: e.target.value })
            }
            required
            disabled={isLoading}
          />

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
          <p>&copy; 2024 COMS. All rights reserved.</p>
        </div>
      </Card>
    </div>
  );
}
