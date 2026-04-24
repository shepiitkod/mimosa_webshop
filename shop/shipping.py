"""
Weight- and zone-based shipping rules (Mimosa Atelier).
Keep in sync with static/shipping.js behaviour; client payload is built from SHIPPING_CLIENT_PAYLOAD.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

# EU-27 except France (France is its own zone).
EU_WITHOUT_FR: frozenset[str] = frozenset(
	{
		'AT',
		'BE',
		'BG',
		'HR',
		'CY',
		'CZ',
		'DK',
		'EE',
		'FI',
		'DE',
		'GR',
		'HU',
		'IE',
		'IT',
		'LV',
		'LT',
		'LU',
		'MT',
		'NL',
		'PL',
		'PT',
		'RO',
		'SK',
		'SI',
		'ES',
		'SE',
	}
)

FREE_SHIPPING_THRESHOLD_EUR = Decimal('85')

# Above this total cart weight (grams), standard carrier matrix is disabled; use oversized block pricing.
MAX_STANDARD_WEIGHT_G = 2000
OVERSIZED_CARRIER = 'oversized'

# Prices by zone key -> carrier id -> [ <500g, 500g–1kg, 1–2kg ] in EUR.
# International Colissimo: only 500g–1kg and 1–2kg were specified; <500g uses 25€ (between EU and mid tier).
PRICES_EUR: dict[str, dict[str, list[int]]] = {
	'FR': {
		'chronopost': [7, 13, 15],
		'colissimo': [6, 10, 12],
		'mondial_relay': [5, 6, 7],
	},
	'EU': {
		'chronopost': [10, 14, 27],
		'colissimo': [8, 12, 23],
	},
	'INTL': {
		'chronopost': [36, 41, 61],
		'colissimo': [25, 29, 54],
	},
}

CARRIER_LABELS: dict[str, dict[str, str]] = {
	'chronopost': {'name': 'Chronopost Express', 'eta': 'Express 24h'},
	'colissimo': {'name': 'Colissimo', 'eta': 'Standard 2–3 jours'},
	'mondial_relay': {'name': 'Mondial Relay', 'eta': 'Point relais 2–4 jours'},
	OVERSIZED_CARRIER: {
		'name': 'Colis lourd (+2 kg)',
		'eta': 'Tarif majoré par tranche de 2 kg (base Colissimo)',
	},
}

# ISO2 -> English label for checkout dropdown (curated; expand as needed).
DESTINATION_COUNTRIES: list[tuple[str, str]] = [
	('FR', 'France'),
	('AT', 'Austria'),
	('BE', 'Belgium'),
	('BG', 'Bulgaria'),
	('HR', 'Croatia'),
	('CY', 'Cyprus'),
	('CZ', 'Czechia'),
	('DK', 'Denmark'),
	('EE', 'Estonia'),
	('FI', 'Finland'),
	('DE', 'Germany'),
	('GR', 'Greece'),
	('HU', 'Hungary'),
	('IE', 'Ireland'),
	('IT', 'Italy'),
	('LV', 'Latvia'),
	('LT', 'Lithuania'),
	('LU', 'Luxembourg'),
	('MT', 'Malta'),
	('NL', 'Netherlands'),
	('PL', 'Poland'),
	('PT', 'Portugal'),
	('RO', 'Romania'),
	('SK', 'Slovakia'),
	('SI', 'Slovenia'),
	('ES', 'Spain'),
	('SE', 'Sweden'),
	('CH', 'Switzerland'),
	('GB', 'United Kingdom'),
	('US', 'United States'),
	('CA', 'Canada'),
	('AU', 'Australia'),
	('UA', 'Ukraine'),
	('JP', 'Japan'),
	('KR', 'South Korea'),
	('NZ', 'New Zealand'),
	('MX', 'Mexico'),
	('BR', 'Brazil'),
	('AE', 'United Arab Emirates'),
	('SG', 'Singapore'),
]


def resolve_zone(country_iso2: str) -> str | None:
	code = (country_iso2 or '').strip().upper()
	if not code or len(code) != 2:
		return None
	if code == 'FR':
		return 'FR'
	if code in EU_WITHOUT_FR:
		return 'EU'
	return 'INTL'


def weight_band_index(total_grams: int) -> int:
	if total_grams < 500:
		return 0
	if total_grams < 1000:
		return 1
	return 2


def carriers_for_zone(zone: str) -> list[str]:
	if zone == 'FR':
		return ['chronopost', 'colissimo', 'mondial_relay']
	if zone in ('EU', 'INTL'):
		return ['chronopost', 'colissimo']
	return []


def carriers_for_cart(zone: str, total_weight_g: int) -> list[str]:
	"""Carriers offered for checkout; heavy carts only use the oversized synthetic carrier."""
	if total_weight_g > MAX_STANDARD_WEIGHT_G:
		return [OVERSIZED_CARRIER]
	return carriers_for_zone(zone)


def oversized_shipping_eur(zone: str, total_weight_g: int) -> Decimal:
	"""Per tranche of 2 kg, Colissimo max-tier price (band 2). Matches frontend oversizedChargeEur."""
	if total_weight_g <= MAX_STANDARD_WEIGHT_G:
		return Decimal('0')
	blocks = (int(total_weight_g) + 1999) // 2000
	base = base_price_eur(zone, 'colissimo', 2)
	return (base * Decimal(blocks)).quantize(Decimal('0.01'))


def base_price_eur(zone: str, carrier: str, band: int) -> Decimal:
	row = PRICES_EUR.get(zone, {}).get(carrier)
	if not row:
		raise ValueError('Unknown zone/carrier')
	b = min(max(band, 0), len(row) - 1)
	return Decimal(row[b])


def is_free_standard_shipping(zone: str, carrier: str, subtotal: Decimal) -> bool:
	if zone != 'FR':
		return False
	if subtotal < FREE_SHIPPING_THRESHOLD_EUR:
		return False
	return carrier in ('colissimo', 'mondial_relay')


def charged_amount_eur(zone: str, carrier: str, band: int, subtotal: Decimal) -> Decimal:
	base = base_price_eur(zone, carrier, band)
	if is_free_standard_shipping(zone, carrier, subtotal):
		return Decimal('0')
	return base


def quote_shipping(country_iso2: str, carrier: str, total_weight_g: int, subtotal: Decimal) -> tuple[Decimal, str | None]:
	"""
	Return (shipping_eur, error_message). error_message set if selection invalid.
	"""
	zone = resolve_zone(country_iso2)
	if zone is None:
		return Decimal('0'), 'Invalid destination country.'

	carrier = (carrier or '').strip().lower()

	if total_weight_g < 1:
		total_weight_g = 1

	allowed = carriers_for_cart(zone, total_weight_g)
	if carrier not in allowed:
		return Decimal('0'), 'This carrier is not available for the selected country or cart weight.'

	if carrier == OVERSIZED_CARRIER:
		amount = oversized_shipping_eur(zone, total_weight_g)
		if amount <= 0:
			return Decimal('0'), 'Unable to quote shipping for this cart. Please contact us.'
		return amount, None

	band = weight_band_index(total_weight_g)
	amount = charged_amount_eur(zone, carrier, band, subtotal)
	return amount.quantize(Decimal('0.01')), None


def stripe_shipping_countries() -> list[str]:
	"""ISO2 list for Stripe Checkout shipping_address_collection."""
	return sorted({code for code, _ in DESTINATION_COUNTRIES})


def client_payload() -> dict[str, Any]:
	"""JSON-serializable rules for the cart page (embedded in template)."""
	groups: dict[str, list[dict[str, str]]] = {'FR': [], 'EU': [], 'INTL': []}
	for iso, label in DESTINATION_COUNTRIES:
		z = resolve_zone(iso)
		if not z:
			continue
		if z == 'FR':
			groups['FR'].append({'iso': iso, 'label': label})
		elif z == 'EU':
			groups['EU'].append({'iso': iso, 'label': label})
		else:
			groups['INTL'].append({'iso': iso, 'label': label})

	for key in groups:
		groups[key].sort(key=lambda x: x['label'].lower())

	return {
		'freeShippingThresholdEur': float(FREE_SHIPPING_THRESHOLD_EUR),
		'maxStandardWeightG': MAX_STANDARD_WEIGHT_G,
		'oversizedCarrierId': OVERSIZED_CARRIER,
		'pricesEur': PRICES_EUR,
		'carrierMeta': CARRIER_LABELS,
		'countryGroups': groups,
	}
