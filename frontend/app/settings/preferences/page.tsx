'use client';

import { type ChangeEvent, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Palette, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface UIPreferences {
  theme: 'light' | 'dark' | 'auto';
  timezone: string;
  language: string;
  compact_mode: boolean;
}

interface ExchangeRatesResponse {
  base: string;
  rates: Record<string, number>;
  source: 'live' | 'fallback';
  timestamp: string;
}

const TIMEZONES = [
  'UTC',
  'Africa/Nairobi',
  'Africa/Johannesburg',
  'Europe/London',
  'America/New_York',
  'Asia/Bangkok',
];

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'sw', name: 'Swahili' },
];

const CURRENCY_OPTIONS = [
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'AED', name: 'UAE Dirham' },
  { code: 'ZAR', name: 'South African Rand' },
  { code: 'UGX', name: 'Ugandan Shilling' },
  { code: 'TZS', name: 'Tanzanian Shilling' },
  { code: 'NGN', name: 'Nigerian Naira' },
  { code: 'INR', name: 'Indian Rupee' },
  { code: 'CNY', name: 'Chinese Yuan' },
];

const QUICK_RATE_CODES = ['USD', 'EUR', 'GBP', 'AED', 'ZAR', 'UGX'];

const DEFAULT_PREFS: UIPreferences = {
  theme: 'light',
  timezone: 'Africa/Nairobi',
  language: 'en',
  compact_mode: false,
};

export default function PreferencesPage() {
  const queryClient = useQueryClient();
  const [activePrefs, setActivePrefs] = useState<UIPreferences | null>(null);
  const [converterAmount, setConverterAmount] = useState('1000');
  const [targetCurrency, setTargetCurrency] = useState('USD');

  const { data: savedPrefs, isLoading } = useQuery<UIPreferences>({
    queryKey: ['ui-preferences'],
    queryFn: async () => {
      const res = await fetch('/api/auth/ui-preferences/', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch preferences');
      return res.json();
    },
  });

  const {
    data: exchangeRates,
    isLoading: ratesLoading,
    refetch: refetchRates,
  } = useQuery<ExchangeRatesResponse>({
    queryKey: ['exchange-rates', 'KES'],
    queryFn: async () => {
      const res = await fetch('/api/exchange-rates/?base=KES', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch exchange rates');
      return res.json();
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (data: UIPreferences) => {
      const res = await fetch('/api/auth/ui-preferences/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save preferences');
      return res.json();
    },
    onSuccess: (data: UIPreferences) => {
      setActivePrefs(null);
      queryClient.setQueryData(['ui-preferences'], data);
    },
  });

  const handleChange = (field: keyof UIPreferences, value: any) => {
    if (!activePrefs && savedPrefs) {
      setActivePrefs({ ...savedPrefs, [field]: value });
    } else if (activePrefs) {
      setActivePrefs({ ...activePrefs, [field]: value });
    }
  };

  const handleSave = async () => {
    if (activePrefs) {
      await saveMutation.mutateAsync(activePrefs);
    }
  };

  const prefs = activePrefs || savedPrefs || DEFAULT_PREFS;
  const normalizedAmount = Number(converterAmount) || 0;
  const targetRate = exchangeRates?.rates?.[targetCurrency] ?? 0;
  const convertedAmount = normalizedAmount * targetRate;

  useEffect(() => {
    if (!prefs?.theme) return;

    const root = document.documentElement;
    const shouldUseDark =
      prefs.theme === 'dark' ||
      (prefs.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    root.classList.toggle('dark', shouldUseDark);
    root.setAttribute('data-theme', prefs.theme);
  }, [prefs?.theme]);

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-3xl font-bold">Preferences</h1>
          <p className="text-gray-600">Customize your user interface experience</p>
        </div>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Palette className="h-5 w-5" /> Appearance
          </h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold mb-2">Theme</label>
              <div className="space-y-2">
                {(['light', 'dark', 'auto'] as const).map((theme) => (
                  <label key={theme} className="flex items-center">
                    <input
                      type="radio"
                      name="theme"
                      value={theme}
                      checked={prefs?.theme === theme}
                      onChange={(e: ChangeEvent<HTMLInputElement>) =>
                        handleChange('theme', e.target.value as UIPreferences['theme'])
                      }
                      className="rounded"
                    />
                    <span className="ml-3 capitalize">{theme}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Localization</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Timezone</label>
              <select
                value={prefs?.timezone || ''}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('timezone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Language</label>
              <select
                value={prefs?.language || ''}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('language', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Compact Mode</p>
              <p className="text-sm text-gray-600">Use a more compact layout throughout the interface</p>
            </div>
            <input
              type="checkbox"
              checked={!!prefs?.compact_mode}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('compact_mode', e.target.checked)}
              className="w-5 h-5"
            />
          </label>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold">Currency Conversion</h2>
              <p className="text-sm text-gray-600">
                Kenyan Shilling is the default base currency. Convert KES amounts into other currencies using the live exchange-rate API.
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => refetchRates()}
              disabled={ratesLoading}
              leftIcon={<RefreshCw className={ratesLoading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />}
            >
              Refresh
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Input
              label="Amount in KES"
              type="number"
              min="0"
              step="0.01"
              value={converterAmount}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConverterAmount(e.target.value)}
              helperText="Base currency is fixed to Kenyan Shilling."
            />

            <div>
              <label className="block text-sm font-semibold mb-2">Convert To</label>
              <select
                value={targetCurrency}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => setTargetCurrency(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {CURRENCY_OPTIONS.map((currency) => (
                  <option key={currency.code} value={currency.code}>
                    {currency.code} - {currency.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <p className="text-sm text-gray-600 mb-1">Converted amount</p>
            <p className="text-2xl font-bold text-gray-900">
              {targetCurrency} {convertedAmount.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              1 KES = {targetRate.toLocaleString(undefined, { maximumFractionDigits: 4 })} {targetCurrency}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Source: {exchangeRates?.source || 'loading'}
              {exchangeRates?.timestamp ? ` • Updated ${new Date(exchangeRates.timestamp).toLocaleString()}` : ''}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {QUICK_RATE_CODES.map((code) => (
              <div key={code} className="rounded-lg border border-gray-200 p-3">
                <p className="text-sm text-gray-600">KES to {code}</p>
                <p className="text-lg font-semibold text-gray-900">
                  {(exchangeRates?.rates?.[code] ?? 0).toLocaleString(undefined, {
                    maximumFractionDigits: 4,
                  })}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {activePrefs && (
          <div className="flex gap-2 pt-4 border-t">
            <Button onClick={handleSave} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving...' : 'Save Preferences'}
            </Button>
            <Button variant="outline" onClick={() => setActivePrefs(null)}>
              Cancel
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
