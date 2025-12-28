


"""Context processors for home app."""
from converter.utils import get_all_tools

def site_info(request):
    """Add site information to all templates."""
    return {
        'site_name': 'PDF Converter Pro',
        'all_tools': get_all_tools(),
        'current_year': 2024,
    }