import datetime
from functools import partial
from random import choice

from django import forms
from django.conf.urls import url
from django.views.generic import FormView

from govuk_forms.fields import SplitDateField
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import InlineCheckboxSelectMultiple, InlineRadioSelect, \
    SeparatedCheckboxSelectMultiple, SeparatedRadioSelect

options = (('a', 'Alpha'), ('b', 'Beta'))
separated_options = (('a', 'Alpha'), ('b', 'Beta'), ('c', 'Gamma'), ('d', 'Delta'), ('e', 'Epsilon'))
grouped_options = (
    ('First', options),
    ('Second', (('c', 'Gamma'), ('d', 'Delta'))),
)
random_option = partial(choice, ['a', 'b'])
random_separated = partial(choice, ['a', 'b', 'c', 'd', 'e'])
random_grouped = partial(choice, ['a', 'b', 'c', 'd'])


class DemoForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'
    prefix = 'demo'

    text = forms.CharField(label='Some required text')
    text_optional = forms.CharField(label='Some optional text', required=False)
    text_with_hint = forms.CharField(label='Some text', required=False, help_text='A hint describing this field')
    number = forms.IntegerField(label='A number', required=False, min_value=1, max_value=10)
    email = forms.EmailField(label='E-mail address')
    url = forms.URLField(label='Link')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    textarea = forms.CharField(label='Larger text', help_text='Hint message', required=False, widget=forms.Textarea)

    date = forms.DateField(label='Date', required=False)
    datetime_ = forms.DateTimeField(label='Date/time', required=False)
    time = forms.TimeField(label='Time', required=False)
    split_date = SplitDateField(label='Split date', required=False)
    split_datetime = forms.SplitDateTimeField(label='Split date/time', required=False)
    date_select = forms.DateField(label='Select date', required=False, widget=forms.SelectDateWidget)
    date_select_required = forms.DateField(label='Select date required', widget=forms.SelectDateWidget)

    select = forms.ChoiceField(label='Selection', choices=options)
    select_groups = forms.ChoiceField(label='Selection with groups', required=False, choices=grouped_options)
    select_multiple = forms.MultipleChoiceField(label='Multiple selection', choices=grouped_options)

    yes_no = forms.BooleanField(label='Yes/no')
    yes_no_null = forms.NullBooleanField(label='Yes/no/null', required=False)

    check = forms.ChoiceField(label='Checkboxes', choices=options, widget=forms.CheckboxSelectMultiple)
    check_inline = forms.ChoiceField(label='Checkboxes inline', choices=options, widget=InlineCheckboxSelectMultiple)
    check_separated = forms.ChoiceField(label='Checkboxes separated', choices=separated_options,
                                        widget=SeparatedCheckboxSelectMultiple)
    check_grouped = forms.ChoiceField(label='Checkboxes with groups', choices=grouped_options,
                                      widget=forms.CheckboxSelectMultiple)
    radio = forms.ChoiceField(label='Radio', choices=options, widget=forms.RadioSelect)
    radio_inline = forms.ChoiceField(label='Radio inline', choices=options, widget=InlineRadioSelect)
    radio_separated = forms.ChoiceField(label='Radio separated', choices=separated_options, widget=SeparatedRadioSelect)
    radio_grouped = forms.ChoiceField(label='Radio with groups', choices=grouped_options, widget=forms.RadioSelect)

    hidden = forms.CharField(label='Hidden', widget=forms.HiddenInput)

    file = forms.FileField(label='Upload a file', widget=forms.FileInput)
    clearable_file = forms.FileField(label='Clearable upload a file')


class FakeFile:
    url = '#file.txt'

    def __str__(self):
        return 'file.txt'


app_name = 'demo'
view = partial(FormView.as_view, form_class=DemoForm, template_name='demo_service/demo.html')
urlpatterns = [
    url(r'^$', view(success_url='demo:empty'), name='empty'),

    url(r'^with-data/$', view(success_url='demo:with-data', initial={
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
    }), name='with-data'),
]
