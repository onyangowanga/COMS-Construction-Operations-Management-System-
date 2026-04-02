"""Exchange rate endpoint with KES default base currency."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


FALLBACK_RATES = {
    'USD': 0.0077,
    'EUR': 0.0071,
    'GBP': 0.0061,
    'JPY': 1.15,
    'CAD': 0.0104,
    'AUD': 0.0117,
    'ZAR': 0.14,
    'UGX': 28.8,
    'TZS': 20.3,
    'NGN': 11.9,
    'INR': 0.64,
    'AED': 0.028,
    'CNY': 0.056,
    'KES': 1.0,
}


class ExchangeRateView(APIView):
    """Return FX rates from a base currency (defaults to KES)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        base = str(request.query_params.get('base', 'KES')).upper()
        symbols_param = request.query_params.get('symbols', '')
        symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]

        rates = self._fetch_live_rates(base, symbols)
        source = 'live'

        if rates is None:
            source = 'fallback'
            rates = self._fallback_rates(base, symbols)

        return Response(
            {
                'base': base,
                'rates': rates,
                'source': source,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
        )

    def _fetch_live_rates(self, base: str, symbols: list[str]) -> dict[str, float] | None:
        try:
            params = {'base': base}
            if symbols:
                params['symbols'] = ','.join(symbols)
            url = f"https://api.exchangerate.host/latest?{urlencode(params)}"
            with urlopen(url, timeout=4) as response:
                payload = json.loads(response.read().decode('utf-8'))
            if not payload.get('success', False) and 'rates' not in payload:
                return None
            rates = payload.get('rates') or {}
            return {k: float(v) for k, v in rates.items()}
        except Exception:
            return None

    def _fallback_rates(self, base: str, symbols: list[str]) -> dict[str, float]:
        base_to_kes = FALLBACK_RATES.get(base)
        if not base_to_kes:
            base_to_kes = 1.0 if base == 'KES' else FALLBACK_RATES['KES']

        if symbols:
            pool = {code: FALLBACK_RATES.get(code) for code in symbols}
        else:
            pool = FALLBACK_RATES

        rates = {}
        for code, kes_rate in pool.items():
            if kes_rate is None:
                continue
            if base == 'KES':
                rates[code] = float(kes_rate)
            else:
                rates[code] = float(kes_rate / base_to_kes)
        return rates
