"""Helper to load Ansible filters for testing"""


def load_core_filters():
    """Load all Ansible core filters"""
    try:
        from ansible.plugins.filter.core import FilterModule

        return FilterModule().filters()
    except ImportError:
        # Ansible not installed, return empty dict
        return {}
