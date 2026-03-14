"""
Unit tests for prompt loader utility

Tests Requirement 13.1 and 13.2:
- Load prompts from /prompts/v1/ directory
- Support variable substitution
- Handle missing templates gracefully
"""

import pytest
import tempfile
import os
from pathlib import Path
from app.utils.prompt_loader import PromptLoader, load_prompt, get_prompt_loader


@pytest.fixture
def prompts_dir(tmp_path):
    """Create a temporary prompts directory with test templates"""
    d = tmp_path / "prompts" / "v1"
    d.mkdir(parents=True)

    (d / "signal-invoice.md").write_text(
        "# Invoice Extraction Prompt\nExtract valid JSON only from the invoice."
    )
    (d / "signal-email.md").write_text(
        "# Email Classification Prompt\nClassify the email."
    )
    (d / "risk-diagnosis.md").write_text("Diagnose risk.")
    (d / "strategy-planning.md").write_text("Plan strategy.")
    (d / "reeval.md").write_text("Re-evaluate outcome.")
    (d / "voice.md").write_text("Voice briefing template.")
    return str(d)


class TestPromptLoader:
    """Test suite for PromptLoader class"""

    def test_load_prompt_without_variables(self, prompts_dir):
        loader = PromptLoader(prompts_dir)
        prompt = loader.load_prompt("signal-invoice")

        assert prompt is not None
        assert len(prompt) > 0
        assert "Invoice Extraction Prompt" in prompt
        assert "valid JSON only" in prompt

    def test_load_prompt_with_variables(self, prompts_dir):
        test_path = Path(prompts_dir) / "test-template.md"
        test_path.write_text("Hello {name}, your score is {score}.")

        loader = PromptLoader(prompts_dir)
        prompt = loader.load_prompt("test-template", variables={
            "name": "Alice",
            "score": 95,
        })

        assert "Hello Alice" in prompt
        assert "your score is 95" in prompt

    def test_load_prompt_missing_template(self, prompts_dir):
        loader = PromptLoader(prompts_dir)
        with pytest.raises(FileNotFoundError):
            loader.load_prompt("nonexistent-template")

    def test_load_prompt_missing_variable(self, prompts_dir):
        test_path = Path(prompts_dir) / "test-vars.md"
        test_path.write_text("Hello {name}, your score is {score}.")

        loader = PromptLoader(prompts_dir)
        with pytest.raises(KeyError):
            loader.load_prompt("test-vars", variables={"name": "Bob"})

    def test_list_templates(self, prompts_dir):
        loader = PromptLoader(prompts_dir)
        templates = loader.list_templates()

        assert len(templates) > 0
        assert "signal-invoice" in templates
        assert "signal-email" in templates
        assert "risk-diagnosis" in templates
        assert "strategy-planning" in templates
        assert "reeval" in templates
        assert "voice" in templates

    def test_singleton_pattern(self, prompts_dir, monkeypatch):
        import app.utils.prompt_loader as pl
        pl._prompt_loader = None
        monkeypatch.setattr(pl, "_prompt_loader", None)

        # Patch default dir so singleton can init
        monkeypatch.setattr(pl.PromptLoader, "__init__", lambda self, d=prompts_dir: (
            setattr(self, "prompts_dir", Path(d)) or None
        ))

        loader1 = get_prompt_loader()
        loader2 = get_prompt_loader()
        assert loader1 is loader2

    def test_convenience_function(self, prompts_dir, monkeypatch):
        import app.utils.prompt_loader as pl
        pl._prompt_loader = PromptLoader(prompts_dir)

        prompt = load_prompt("signal-email")
        assert prompt is not None
        assert "Email Classification Prompt" in prompt

    def test_all_required_templates_exist(self, prompts_dir):
        loader = PromptLoader(prompts_dir)
        required = [
            "signal-invoice", "signal-email", "risk-diagnosis",
            "strategy-planning", "reeval", "voice",
        ]
        for name in required:
            prompt = loader.load_prompt(name)
            assert prompt is not None
            assert len(prompt) > 0
