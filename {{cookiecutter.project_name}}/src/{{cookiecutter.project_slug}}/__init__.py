"""
{{ cookiecutter.project_name }} init
"""

__maintainer__ = "{{ cookiecutter.company_name }}"
{% if cookiecutter.license == 'NONE' -%}
__copyright__ = "(c) {{ cookiecutter.company_name }}"
{% elif cookiecutter.license == 'MIT' -%}
__license__ = "MIT"
{% elif cookiecutter.license == 'BSD-3' -%}
__license__ = "BSD-3-Clause"
{% endif -%}
__project_name__ = "{{ cookiecutter.project_slug }}"
__version__ = "0.0.0"
