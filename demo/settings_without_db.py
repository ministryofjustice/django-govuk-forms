from settings import *  # noqa

DATABASES = {}

GOVUK_SERVICE_SETTINGS = {
    'name': 'Demo service',
    'phase': 'alpha',
    'header_links': [
        {'name': 'Simple', 'link': 'demo:simple', 'link_is_view_name': True},
        {'name': 'Long', 'link': 'demo:long', 'link_is_view_name': True},
        {'name': 'Pre-filled', 'link': 'demo:prefilled', 'link_is_view_name': True},
        {'name': 'Field sets', 'link': 'demo:fieldsets', 'link_is_view_name': True},
        {'name': 'Conditionally revealed', 'link': 'demo:revealing', 'link_is_view_name': True},
    ],
}
