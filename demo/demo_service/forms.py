from django import forms

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


class SimpleForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    name = forms.CharField()
    email = forms.EmailField()


class LongForm(GOVUKForm):
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

    check = forms.MultipleChoiceField(label='Checkboxes', choices=options, widget=forms.CheckboxSelectMultiple)
    check_inline = forms.MultipleChoiceField(label='Checkboxes inline', choices=options,
                                             widget=InlineCheckboxSelectMultiple)
    check_separated = forms.MultipleChoiceField(label='Checkboxes separated', choices=separated_options,
                                                widget=SeparatedCheckboxSelectMultiple)
    check_grouped = forms.MultipleChoiceField(label='Checkboxes with groups', choices=grouped_options,
                                              widget=forms.CheckboxSelectMultiple)
    radio = forms.ChoiceField(label='Radio', choices=options, widget=forms.RadioSelect)
    radio_inline = forms.ChoiceField(label='Radio inline', choices=options, widget=InlineRadioSelect)
    radio_separated = forms.ChoiceField(label='Radio separated', choices=separated_options, widget=SeparatedRadioSelect)
    radio_grouped = forms.ChoiceField(label='Radio with groups', choices=grouped_options, widget=forms.RadioSelect)

    hidden = forms.CharField(label='Hidden', widget=forms.HiddenInput)

    file = forms.FileField(label='Upload a file', widget=forms.FileInput)
    clearable_file = forms.FileField(label='Clearable upload a file')


class FieldsetForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True
    fieldsets = [
        ['Enter your name', ['first_name', 'last_name']],
        ['Enter your address', ['address', 'city', 'postcode', 'country']],
    ]

    last_name = forms.CharField(label='Surname')
    first_name = forms.CharField(label='First name')

    email = forms.EmailField(label='E-mail address', help_text='We will only use this to send you a receipt')

    address = forms.CharField(label='Street', help_text='Include your flat or building number')
    city = forms.CharField(label='City')
    postcode = forms.CharField(label='Postcode')
    country = forms.CharField(label='Country')


class RevealingForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True
    reveal_conditionally = {
        'show': {True: 'hidden_at_first'},
        'choices': {
            'a': 'hidden_at_first_a',
            'b': 'hidden_at_first_b',
            'd': 'hidden_at_first_d',
        },
    }

    show = forms.BooleanField(label='Show', required=False)
    hidden_at_first = forms.CharField(label='Hidden at first')

    choices = forms.ChoiceField(label='More options', choices=separated_options, widget=forms.RadioSelect)
    hidden_at_first_a = forms.EmailField(label='Email')
    hidden_at_first_b = forms.IntegerField(label='Number')
    hidden_at_first_d = SplitDateField(label='Split date')
