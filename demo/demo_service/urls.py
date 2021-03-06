import datetime
from functools import partial
from random import choice

from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import FormView

from demo_service.forms import SimpleForm, LongForm, FieldsetForm, RevealingForm

random_option = partial(choice, ['a', 'b'])
random_separated = partial(choice, ['a', 'b', 'c', 'd', 'e'])
random_grouped = partial(choice, ['a', 'b', 'c', 'd'])


class FakeFile:
    url = '#file.txt'

    def __str__(self):
        return 'file.txt'


app_name = 'demo'
view = partial(FormView.as_view, template_name='demo_service/demo.html')
urlpatterns = [
    url(r'^$', view(form_class=SimpleForm, success_url=reverse_lazy('demo:simple')), name='simple'),
    url(r'^long/$', view(form_class=LongForm, success_url=reverse_lazy('demo:long')), name='long'),
    url(r'^prefilled/$', view(form_class=LongForm, success_url=reverse_lazy('demo:prefilled'), initial={
        'text': 'sample', 'text_optional': 'not necessary', 'text_with_hint': 'hint helped',
        'email': 'example@gov.uk', 'url': 'gov.uk', 'password': '1234',
        'number': 123, 'textarea': '\nLorem ipsum\n',
        'date': datetime.date.today(), 'datetime_': datetime.datetime.now(), 'time': datetime.datetime.now().time(),
        'split_date': datetime.date.today(), 'split_datetime': datetime.datetime.now(),
        'date_select': datetime.date.today(), 'date_select_required': datetime.date.today(),
        'select': random_option(), 'select_groups': random_grouped(), 'select_multiple': [random_grouped()],
        'yes_no': True, 'yes_no_null': False,
        'check': random_option(), 'check_inline': random_option(), 'check_separated': random_separated(),
        'check_grouped': random_grouped(),
        'radio': random_option(), 'radio_inline': random_option(), 'radio_separated': random_separated(),
        'radio_grouped': random_grouped(),
        'hidden': 'secret',
        'file': FakeFile(), 'clearable_file': FakeFile(),
    }), name='prefilled'),
    url(r'^fieldsets/$', view(form_class=FieldsetForm, success_url=reverse_lazy('demo:fieldsets')), name='fieldsets'),
    url(r'^revealing/$', view(form_class=RevealingForm, success_url=reverse_lazy('demo:revealing'), initial={
        'choices': 'b',
    }), name='revealing'),
]
