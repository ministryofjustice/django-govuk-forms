from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FormsAppConfig(AppConfig):
    name = 'govuk_forms'
    verbose_name = _('GOV.UK Forms')
