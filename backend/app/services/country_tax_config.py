"""
Country-specific tax configuration — rates, thresholds, and filing rules.

Supports multi-country tax calculations. Each country config includes:
- CIT thresholds and rates
- VAT/GST rate
- WHT rates
- PAYE rules
- Filing deadlines and penalties
- Currency and dialling code
"""

from typing import Any, Dict, List, Tuple

# Country configs keyed by ISO 3166-1 alpha-2 code
COUNTRY_TAX_CONFIG: Dict[str, Dict[str, Any]] = {
    "NG": {
        "name": "Nigeria",
        "currency": "NGN",
        "currency_symbol": "₦",
        "dial_code": "+234",
        "flag": "🇳🇬",
        "tax_authority": "FIRS (Federal Inland Revenue Service)",
        "cit_thresholds": [
            (25_000_000, 0.0, "Exempt (turnover ≤ ₦25M) — 0% CIT"),
            (100_000_000, 0.20, "Medium company (₦25M–₦100M) — 20% CIT"),
            (float("inf"), 0.30, "Large company (> ₦100M) — 30% CIT"),
        ],
        "vat_rate": 0.075,
        "vat_name": "VAT",
        "wht_rate_services": 0.05,
        "wht_rate_goods": 0.05,
        "paye_tax_free_threshold": 800_000,
        "paye_avg_rate": 0.15,
        "filing_deadline_cit": "June 30 of the following year",
        "filing_deadline_vat": "21st of the following month",
        "late_filing_penalty": "₦25,000 first month + ₦5,000 each subsequent month",
        "late_payment_penalty": "10% penalty + interest at CBN rate",
    },
    "GH": {
        "name": "Ghana",
        "currency": "GHS",
        "currency_symbol": "GH₵",
        "dial_code": "+233",
        "flag": "🇬🇭",
        "tax_authority": "GRA (Ghana Revenue Authority)",
        "cit_thresholds": [
            (float("inf"), 0.25, "Standard CIT rate — 25%"),
        ],
        "vat_rate": 0.15,
        "vat_name": "VAT + NHIL + GETFund + COVID levy",
        "wht_rate_services": 0.05,
        "wht_rate_goods": 0.03,
        "paye_tax_free_threshold": 4_380,  # GHS annual
        "paye_avg_rate": 0.20,
        "filing_deadline_cit": "April 30 of the following year",
        "filing_deadline_vat": "Last working day of the following month",
        "late_filing_penalty": "GH₵500 + 5% of tax due per month",
        "late_payment_penalty": "25% surcharge + interest at 125% of BoG rate",
    },
    "KE": {
        "name": "Kenya",
        "currency": "KES",
        "currency_symbol": "KSh",
        "dial_code": "+254",
        "flag": "🇰🇪",
        "tax_authority": "KRA (Kenya Revenue Authority)",
        "cit_thresholds": [
            (float("inf"), 0.30, "Standard CIT rate — 30%"),
        ],
        "vat_rate": 0.16,
        "vat_name": "VAT",
        "wht_rate_services": 0.05,
        "wht_rate_goods": 0.03,
        "paye_tax_free_threshold": 288_000,  # KES annual (24k/month)
        "paye_avg_rate": 0.25,
        "filing_deadline_cit": "6 months after end of accounting period",
        "filing_deadline_vat": "20th of the following month",
        "late_filing_penalty": "KSh 10,000 per month or 5% of tax due",
        "late_payment_penalty": "20% of tax due + 2% per month interest",
    },
    "ZA": {
        "name": "South Africa",
        "currency": "ZAR",
        "currency_symbol": "R",
        "dial_code": "+27",
        "flag": "🇿🇦",
        "tax_authority": "SARS (South African Revenue Service)",
        "cit_thresholds": [
            (float("inf"), 0.27, "Standard CIT rate — 27%"),
        ],
        "vat_rate": 0.15,
        "vat_name": "VAT",
        "wht_rate_services": 0.15,
        "wht_rate_goods": 0.0,
        "paye_tax_free_threshold": 95_750,  # ZAR annual (under 65)
        "paye_avg_rate": 0.25,
        "filing_deadline_cit": "12 months after financial year end",
        "filing_deadline_vat": "25th of the following month",
        "late_filing_penalty": "R250 per month (up to 35 months)",
        "late_payment_penalty": "10% penalty + interest at prescribed rate",
    },
    "RW": {
        "name": "Rwanda",
        "currency": "RWF",
        "currency_symbol": "FRw",
        "dial_code": "+250",
        "flag": "🇷🇼",
        "tax_authority": "RRA (Rwanda Revenue Authority)",
        "cit_thresholds": [
            (float("inf"), 0.30, "Standard CIT rate — 30%"),
        ],
        "vat_rate": 0.18,
        "vat_name": "VAT",
        "wht_rate_services": 0.15,
        "wht_rate_goods": 0.05,
        "paye_tax_free_threshold": 360_000,  # RWF annual (30k/month)
        "paye_avg_rate": 0.20,
        "filing_deadline_cit": "March 31 of the following year",
        "filing_deadline_vat": "15th of the following month",
        "late_filing_penalty": "20% of tax due",
        "late_payment_penalty": "10% penalty + 1.5% per month interest",
    },
    "GB": {
        "name": "United Kingdom",
        "currency": "GBP",
        "currency_symbol": "£",
        "dial_code": "+44",
        "flag": "🇬🇧",
        "tax_authority": "HMRC",
        "cit_thresholds": [
            (50_000, 0.19, "Small profits rate — 19%"),
            (250_000, 0.265, "Marginal relief rate — 26.5%"),
            (float("inf"), 0.25, "Main rate — 25%"),
        ],
        "vat_rate": 0.20,
        "vat_name": "VAT",
        "wht_rate_services": 0.0,
        "wht_rate_goods": 0.0,
        "paye_tax_free_threshold": 12_570,  # GBP personal allowance
        "paye_avg_rate": 0.20,
        "filing_deadline_cit": "12 months after accounting period end",
        "filing_deadline_vat": "1 month + 7 days after VAT period end",
        "late_filing_penalty": "£100 initial + escalating penalties",
        "late_payment_penalty": "Interest at BoE base rate + 2.5%",
    },
}

# Dial codes for phone input (broader list)
DIAL_CODES: List[Dict[str, str]] = [
    {"code": "+234", "country": "NG", "flag": "🇳🇬", "name": "Nigeria"},
    {"code": "+233", "country": "GH", "flag": "🇬🇭", "name": "Ghana"},
    {"code": "+254", "country": "KE", "flag": "🇰🇪", "name": "Kenya"},
    {"code": "+27", "country": "ZA", "flag": "🇿🇦", "name": "South Africa"},
    {"code": "+250", "country": "RW", "flag": "🇷🇼", "name": "Rwanda"},
    {"code": "+255", "country": "TZ", "flag": "🇹🇿", "name": "Tanzania"},
    {"code": "+256", "country": "UG", "flag": "🇺🇬", "name": "Uganda"},
    {"code": "+251", "country": "ET", "flag": "🇪🇹", "name": "Ethiopia"},
    {"code": "+237", "country": "CM", "flag": "🇨🇲", "name": "Cameroon"},
    {"code": "+225", "country": "CI", "flag": "🇨🇮", "name": "Côte d'Ivoire"},
    {"code": "+221", "country": "SN", "flag": "🇸🇳", "name": "Senegal"},
    {"code": "+44", "country": "GB", "flag": "🇬🇧", "name": "United Kingdom"},
    {"code": "+1", "country": "US", "flag": "🇺🇸", "name": "United States"},
    {"code": "+971", "country": "AE", "flag": "🇦🇪", "name": "UAE"},
]


def get_country_config(country_code: str) -> Dict[str, Any]:
    """Get tax config for a country. Falls back to Nigeria if unknown."""
    return COUNTRY_TAX_CONFIG.get(country_code.upper(), COUNTRY_TAX_CONFIG["NG"])


def get_dial_codes() -> List[Dict[str, str]]:
    """Return all supported dial codes for phone input."""
    return DIAL_CODES


def compute_cit(net_profit: float, total_revenue: float, country_code: str = "NG") -> Tuple[float, float, str]:
    """Compute CIT amount, rate, and note for a country.

    Returns: (cit_amount, cit_rate, cit_note)
    """
    config = get_country_config(country_code)
    thresholds = config["cit_thresholds"]

    cit_rate = 0.0
    cit_note = ""
    for threshold, rate, note in thresholds:
        if total_revenue <= threshold:
            cit_rate = rate
            cit_note = note
            break

    cit_amount = round(max(net_profit, 0) * cit_rate, 2)
    return cit_amount, cit_rate, cit_note


def compute_vat(revenue: float, expenses: float, vat_registered: bool, country_code: str = "NG") -> Tuple[float, float, float]:
    """Compute VAT collected, input credit, and payable.

    Returns: (vat_collected, vat_input, vat_payable)
    """
    config = get_country_config(country_code)
    vat_rate = config["vat_rate"]

    if not vat_registered:
        return 0.0, 0.0, 0.0

    vat_collected = round(revenue * vat_rate, 2)
    vat_input = round(expenses * vat_rate * 0.3, 2)  # estimate 30% vatable
    vat_payable = round(max(vat_collected - vat_input, 0), 2)
    return vat_collected, vat_input, vat_payable


def compute_paye(annual_staff_cost: float, has_employees: bool, country_code: str = "NG") -> float:
    """Compute estimated PAYE liability."""
    if not has_employees or annual_staff_cost <= 0:
        return 0.0

    config = get_country_config(country_code)
    threshold = config["paye_tax_free_threshold"]
    avg_rate = config["paye_avg_rate"]

    taxable = max(annual_staff_cost - threshold, 0)
    return round(taxable * avg_rate, 2)
