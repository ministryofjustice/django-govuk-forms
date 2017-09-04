import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _

from govuk_forms.widgets import SplitDateWidget, SplitHiddenDateWidget


class YearField(forms.IntegerField):
    """
    In integer field that accepts years between 1900 and now
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """

    def __init__(self, era_boundary=None, **kwargs):
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        bounds_error = gettext('Year should be between 1900 and %(current_year)s.') % {
            'current_year': self.current_year
        }
        options = {
            'min_value': 1900,
            'max_value': self.current_year,
            'error_messages': {
                'min_value': bounds_error,
                'max_value': bounds_error,
                'invalid': gettext('Enter year as a number.'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        value = self.to_python(value)
        if isinstance(value, int) and value < 100:
            if value > self.era_boundary:
                value += self.century - 100
            else:
                value += self.century
        return super().clean(value)


class SplitDateField(forms.MultiValueField):
    widget = SplitDateWidget
    hidden_widget = SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Enter a valid date.')
    }

    def __init__(self, *args, **kwargs):
        day_bounds_error = gettext('Day should be between 1 and 31.')
        month_bounds_error = gettext('Month should be between 1 and 12.')

        self.fields = [
            forms.IntegerField(min_value=1, max_value=31, error_messages={
                'min_value': day_bounds_error,
                'max_value': day_bounds_error,
                'invalid': gettext('Enter day as a number.')
            }),
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Enter month as a number.')
            }),
            YearField(),
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return datetime.date(data_list[2], data_list[1], data_list[0])
            except ValueError:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, SplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs
