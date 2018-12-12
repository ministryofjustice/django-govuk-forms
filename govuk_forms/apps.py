from django.utils.translation import gettext_lazy as _
try:
    from govuk_template_base.apps import BaseAppConfig
except ImportError:
    from django.apps import AppConfig as BaseAppConfig


class FormsAppConfig(BaseAppConfig):
    name = 'govuk_forms'
    verbose_name = _('GOV.UK Forms')
