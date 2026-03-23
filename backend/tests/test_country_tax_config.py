"""Unit tests for country tax configuration and computation functions."""

import pytest
from app.services.country_tax_config import (
    get_country_config, get_dial_codes,
    compute_cit, compute_vat, compute_paye,
)


class TestGetCountryConfig:
    def test_nigeria_config(self):
        config = get_country_config("NG")
        assert config["name"] == "Nigeria"
        assert config["currency"] == "NGN"
        assert config["vat_rate"] == 0.075

    def test_kenya_config(self):
        config = get_country_config("KE")
        assert config["name"] == "Kenya"
        assert config["vat_rate"] == 0.16

    def test_ghana_config(self):
        config = get_country_config("GH")
        assert config["currency"] == "GHS"

    def test_unknown_country_falls_back_to_nigeria(self):
        config = get_country_config("XX")
        assert config["name"] == "Nigeria"

    def test_case_insensitive(self):
        config = get_country_config("ng")
        assert config["name"] == "Nigeria"


class TestComputeCIT:
    def test_nigeria_exempt_small_company(self):
        amount, rate, note = compute_cit(net_profit=5000000, total_revenue=20000000, country_code="NG")
        assert rate == 0.0
        assert amount == 0.0
        assert "Exempt" in note

    def test_nigeria_medium_company(self):
        amount, rate, note = compute_cit(net_profit=10000000, total_revenue=50000000, country_code="NG")
        assert rate == 0.20
        assert amount == 2000000.0

    def test_nigeria_large_company(self):
        amount, rate, note = compute_cit(net_profit=50000000, total_revenue=200000000, country_code="NG")
        assert rate == 0.30
        assert amount == 15000000.0

    def test_kenya_flat_rate(self):
        amount, rate, note = compute_cit(net_profit=1000000, total_revenue=5000000, country_code="KE")
        assert rate == 0.30
        assert amount == 300000.0

    def test_negative_profit_returns_zero(self):
        amount, rate, note = compute_cit(net_profit=-500000, total_revenue=1000000, country_code="NG")
        assert amount == 0.0

    def test_uk_small_profits_rate(self):
        amount, rate, note = compute_cit(net_profit=30000, total_revenue=40000, country_code="GB")
        assert rate == 0.19


class TestComputeVAT:
    def test_vat_registered_nigeria(self):
        collected, input_credit, payable = compute_vat(1000000, 500000, True, "NG")
        assert collected == 75000.0
        assert input_credit == 11250.0  # 500000 * 0.075 * 0.3
        assert payable == 63750.0

    def test_not_vat_registered(self):
        collected, input_credit, payable = compute_vat(1000000, 500000, False, "NG")
        assert collected == 0.0
        assert payable == 0.0

    def test_kenya_vat_rate(self):
        collected, _, _ = compute_vat(1000000, 0, True, "KE")
        assert collected == 160000.0  # 16%

    def test_south_africa_vat_rate(self):
        collected, _, _ = compute_vat(1000000, 0, True, "ZA")
        assert collected == 150000.0  # 15%


class TestComputePAYE:
    def test_no_employees(self):
        assert compute_paye(600000, False, "NG") == 0.0

    def test_zero_staff_cost(self):
        assert compute_paye(0, True, "NG") == 0.0

    def test_nigeria_paye_above_threshold(self):
        # Annual staff cost 2M, threshold 800k, taxable 1.2M, rate 15%
        result = compute_paye(2000000, True, "NG")
        assert result == 180000.0

    def test_nigeria_paye_below_threshold(self):
        result = compute_paye(500000, True, "NG")
        assert result == 0.0

    def test_kenya_paye(self):
        # Annual 1M, threshold 288k, taxable 712k, rate 25%
        result = compute_paye(1000000, True, "KE")
        assert result == 178000.0


class TestGetDialCodes:
    def test_returns_list(self):
        codes = get_dial_codes()
        assert isinstance(codes, list)
        assert len(codes) > 0

    def test_nigeria_included(self):
        codes = get_dial_codes()
        ng = [c for c in codes if c["country"] == "NG"]
        assert len(ng) == 1
        assert ng[0]["code"] == "+234"
