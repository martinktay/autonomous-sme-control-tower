"""
Prompt template loader for versioned prompt files in /prompts/v1/.

Loads .md prompt templates by name, optionally substituting {variables}
using Python str.format(). Keeps prompt logic separate from agent code
as required by the prompt management guidelines.
"""

import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads prompt templates from a directory and substitutes variables.

    Templates are .md files in the prompts directory (default: prompts/v1/).
    Variable substitution uses Python str.format() syntax: {variable_name}.
    """
    
    def __init__(self, prompts_dir: str = "prompts/v1"):
        """
        Initialize prompt loader
        
        Args:
            prompts_dir: Directory containing prompt templates
        """
        self.prompts_dir = Path(prompts_dir)
        if not self.prompts_dir.exists():
            # Try relative to project root (one level up from backend/)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            alt = project_root / prompts_dir
            if alt.exists():
                self.prompts_dir = alt
            else:
                raise FileNotFoundError(f"Prompts directory not found: {prompts_dir}")
    
    def load_prompt(
        self,
        template_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Load a prompt template and substitute variables
        
        Args:
            template_name: Name of the template file (without .md extension)
            variables: Dictionary of variables to substitute in the template
            
        Returns:
            Processed prompt string with variables substituted
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            KeyError: If required variable is missing
        """
        # Construct template path
        template_path = self.prompts_dir / f"{template_name}.md"
        
        # Check if template exists
        if not template_path.exists():
            logger.error(f"Prompt template not found: {template_path}")
            raise FileNotFoundError(f"Prompt template not found: {template_name}")
        
        # Load template content
        try:
            template_content = template_path.read_text(encoding="utf-8")
            logger.info(f"Loaded prompt template: {template_name}")
        except Exception as e:
            logger.error(f"Error reading template {template_name}: {e}")
            raise
        
        # Substitute variables if provided
        if variables:
            try:
                template_content = template_content.format(**variables)
                logger.debug(f"Substituted {len(variables)} variables in template {template_name}")
            except KeyError as e:
                logger.error(f"Missing required variable in template {template_name}: {e}")
                raise KeyError(f"Missing required variable for template {template_name}: {e}")
        
        return template_content
    
    def list_templates(self) -> list[str]:
        """
        List all available prompt templates
        
        Returns:
            List of template names (without .md extension)
        """
        templates = [
            f.stem for f in self.prompts_dir.glob("*.md")
        ]
        logger.info(f"Found {len(templates)} prompt templates")
        return templates


# Singleton instance
_prompt_loader: Optional[PromptLoader] = None
_pl_lock = threading.Lock()


def get_prompt_loader() -> PromptLoader:
    """Get singleton PromptLoader instance (thread-safe, lazy-initialised)."""
    global _prompt_loader
    if _prompt_loader is None:
        with _pl_lock:
            if _prompt_loader is None:
                _prompt_loader = PromptLoader()
    return _prompt_loader


def load_prompt(template_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to load a prompt template
    
    Args:
        template_name: Name of the template file (without .md extension)
        variables: Dictionary of variables to substitute in the template
        
    Returns:
        Processed prompt string
    """
    loader = get_prompt_loader()
    return loader.load_prompt(template_name, variables)
