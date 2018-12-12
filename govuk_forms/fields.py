import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from govuk_forms.widgets import SplitDateWidget, SplitHiddenDateWidget


class YearField(forms.IntegerField):
    """
    In integer field that accepts years between 1900 (or min_value) and now (or max_value)
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """
    default_error_messages = {
        'invalid': _('Enter year as a number.'),
        'bounds': _('Year should be between %(min_value)d and %(max_value)d.'),
    }

    def __init__(self, min_value=None, max_value=None, era_boundary=None, **kwargs):
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        min_value = min_value or 1900
        if min_value < 100:
            raise ValueError('`min_value` must be at least 100')
        max_value = max_value or self.current_year
        kwargs.update(
            min_value=min_value,
            max_value=max_value,
        )
        super().__init__(**kwargs)
        bounds_error = self.error_messages.pop('bounds')
        bounds_error = bounds_error % {
            'min_value': min_value,
            'max_value': max_value,
        }
        self.error_messages['min_value'] = bounds_error
        self.error_messages['max_value'] = bounds_error

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
        'invalid': _('Enter a valid date.'),
        'day_invalid': _('Enter day as a number.'),
        'day_bounds': _('Day should be between 1 and 31.'),
        'month_invalid': _('Enter month as a number.'),
        'month_bounds': _('Month should be between 1 and 12.'),
    }

    def __init__(self, *args, **kwargs):
        self.fields = [
            forms.IntegerField(min_value=1, max_value=31),
            forms.IntegerField(min_value=1, max_value=12),
            YearField(),
        ]
        super().__init__(self.fields, *args, **kwargs)
        errors = self.error_messages
        day_errors = self.fields[0].error_messages
        day_errors['invalid'] = errors.pop('day_invalid')
        day_errors['min_value'] = errors['day_bounds']
        day_errors['max_value'] = errors.pop('day_bounds')
        month_errors = self.fields[1].error_messages
        month_errors['invalid'] = errors.pop('month_invalid')
        month_errors['min_value'] = errors['month_bounds']
        month_errors['max_value'] = errors.pop('month_bounds')

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
