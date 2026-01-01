from typing import Dict, Any, Optional
from string import Template

def render_template(template_str: str, template_data: Dict[str, Any]) -> Optional[str]:
    """
    Renders a template string with the given data.
    Returns the rendered string or None if there's an error.
    """
    if not template_str or not template_data:
        return None

    try:
        template = Template(template_str)
        return template.safe_substitute(template_data)
    except (KeyError, TypeError, ValueError):
        # Gracefully handle cases where the template is invalid or data is missing
        return None
