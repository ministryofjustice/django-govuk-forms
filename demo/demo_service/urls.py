import datetime
from functools import partial
from random import choice

from django.conf.urls import url
from django.views.generic import FormView as BaseFormView, TemplateView

from demo_service.forms import SimpleForm, LongForm, FieldsetForm, RevealingForm

random_option = partial(choice, ['a', 'b'])
random_separated = partial(choice, ['a', 'b', 'c', 'd', 'e'])
random_grouped = partial(choice, ['a', 'b', 'c', 'd'])


class FakeFile:
    url = '#file.txt'

    def __str__(self):
        return 'file.txt'


class FormView(BaseFormView):
    template_name = 'demo_service/form.html'
    success_template_name = 'demo_service/data.html'

    def form_valid(self, form):
        if self.success_url:
            return super().form_valid(form)

        def presentable_value(f):
            value = form.cleaned_data[f.name]
            if hasattr(f.field, 'choices'):
                cc = {}
                for c in f.field.choices:
                    if isinstance(c[1], (list, tuple)):
                        for c in c[1]:
                            cc[c[0]] = c[1]
                    else:
                        cc[c[0]] = c[1]
                value = '\n'.join(
                    str(cc.get(value, '???'))
                    for value in value
                )
            return value

        context = {
            'form_data': [
                (field.label, presentable_value(field))
                for field in form
                if field.name in form.cleaned_data
            ],
        }
        return self.response_class(
            request=self.request,
            context=context,
            template=[self.success_template_name],
            using=self.template_engine,
            content_type=self.content_type
        )


app_name = 'demo'
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='demo_service/start.html'), name='start'),
    url(r'^simple/$', FormView.as_view(form_class=SimpleForm), name='simple'),
    url(r'^long/$', FormView.as_view(form_class=LongForm), name='long'),
    url(r'^prefilled/$', FormView.as_view(form_class=LongForm, initial={
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
    url(r'^fieldsets/$', FormView.as_view(form_class=FieldsetForm), name='fieldsets'),
    url(r'^revealing/$', FormView.as_view(form_class=RevealingForm, initial={
        'hidden_at_first': 'initial value',
        'choices': 'b',
    }), name='revealing'),
]
