import datetime

from django.forms import widgets
from django.utils.dates import MONTHS
from django.utils.translation import gettext_lazy as _

__all__ = (
    'Widget', 'MultiWidget',
    'SplitDateWidget', 'SplitHiddenDateWidget', 'SplitDateTimeWidget', 'SplitHiddenDateTimeWidget',

    'CheckboxInput',
    'CheckboxSelectMultiple', 'InlineCheckboxSelectMultiple', 'SeparatedCheckboxSelectMultiple',
    'RadioSelect', 'InlineRadioSelect', 'SeparatedRadioSelect',

    'TextInput', 'NumberInput', 'EmailInput', 'URLInput', 'PasswordInput', 'Textarea',
    'DateInput', 'DateTimeInput', 'TimeInput',
    'Select', 'NullBooleanSelect', 'SelectMultiple',

    'FileInput', 'ClearableFileInput',
    'SelectDateWidget',
)

group_template_names = (
    (widgets.Select, 'govuk_forms/field.html'),
    ((widgets.MultiWidget, widgets.ChoiceWidget), 'govuk_forms/field-fieldset.html'),
    (widgets.CheckboxInput, 'govuk_forms/field-no-label.html'),
    (widgets.Widget, 'govuk_forms/field.html'),
)


class Widget(widgets.Widget):
    input_classes = 'form-control'
    input_error_classes = 'form-control-error'

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        css_classes = self.input_classes() if callable(self.input_classes) else self.input_classes
        attrs['class'] = ('%s %s' % (attrs.get('class', ''), css_classes)).strip()
        return attrs


class MultiWidget(widgets.MultiWidget, Widget):
    subwidget_group_classes = ()
    subwidget_label_classes = ()
    subwidget_labels = ()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        iterator = zip(context['widget']['subwidgets'],
                       self.subwidget_group_classes,
                       self.subwidget_label_classes,
                       self.subwidget_labels)
        for subwidget, group_classes, label_classes, label in iterator:
            subwidget.update(
                group_classes=group_classes,
                label_classes=label_classes,
                label=label,
            )
        return context

    def decompress(self, value):
        raise NotImplementedError


class SplitDateWidget(MultiWidget):
    template_name = 'govuk_forms/widgets/split-date.html'
    subwidget_group_classes = ('form-group form-group-day',
                               'form-group form-group-month',
                               'form-group form-group-year')
    subwidget_label_classes = ('form-label', 'form-label', 'form-label')  # or form-label-bold
    subwidget_labels = (_('Day'), _('Month'), _('Year'))

    def __init__(self, attrs=None):
        date_widgets = (widgets.NumberInput(attrs=attrs),
                        widgets.NumberInput(attrs=attrs),
                        widgets.NumberInput(attrs=attrs),)
        super().__init__(date_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]


class SplitHiddenDateWidget(SplitDateWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for widget in self.widgets:
            widget.input_type = 'hidden'


class SplitDateTimeWidget(widgets.SplitDateTimeWidget, MultiWidget):
    template_name = 'govuk_forms/widgets/split-date.html'
    subwidget_group_classes = ('form-group form-group-date', 'form-group form-group-time')
    subwidget_label_classes = ('form-label', 'form-label')  # or form-label-bold
    subwidget_labels = (_('Date'), _('Time'))


class SplitHiddenDateTimeWidget(SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for widget in self.widgets:
            widget.input_type = 'hidden'


class CheckboxInput(widgets.CheckboxInput, Widget):
    template_name = 'govuk_forms/widgets/checkbox.html'
    inherit_label_from_field = True
    label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionally_revealed = {}

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.label:
            context['widget']['label'] = self.label
        context['conditionally_revealed'] = self.conditionally_revealed.get(True)
        return context


class ChoiceWidget(widgets.ChoiceWidget, Widget):
    template_name = 'govuk_forms/widgets/multiple-select.html'
    option_template_name = 'govuk_forms/widgets/multiple-select-option.html'
    separate_last_option = False
    last_option_label = _('or')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionally_revealed = {}

    @property
    def is_flat_list(self):
        return not any(isinstance(choice, (tuple, list)) for name, choice in self.choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update(
            is_flat_list=self.is_flat_list,
            separate_last_option=self.separate_last_option,
            last_option_label=self.last_option_label,
        )
        return context

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if self.conditionally_revealed:
            option['conditionally_revealed'] = self.conditionally_revealed.get(value)
        return option


class CheckboxSelectMultiple(ChoiceWidget, widgets.CheckboxSelectMultiple):
    pass


class InlineCheckboxSelectMultiple(CheckboxSelectMultiple):
    field_group_classes = 'inline'


class SeparatedCheckboxSelectMultiple(CheckboxSelectMultiple):
    separate_last_option = True


class RadioSelect(ChoiceWidget, widgets.RadioSelect):
    pass


class InlineRadioSelect(RadioSelect):
    field_group_classes = 'inline'


class SeparatedRadioSelect(RadioSelect):
    separate_last_option = True


class TextInput(widgets.TextInput, Widget):
    pass


class NumberInput(widgets.NumberInput, Widget):
    input_classes = 'form-control form-control-1-8'


class EmailInput(widgets.EmailInput, Widget):
    pass


class URLInput(widgets.URLInput, Widget):
    input_classes = 'form-control form-control-2-3'


class PasswordInput(widgets.PasswordInput, Widget):
    input_classes = 'form-control form-control-1-4'


class Textarea(widgets.Textarea, Widget):
    def __init__(self, attrs=None):
        default_attrs = {'cols': '60', 'rows': '8'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class DateInput(widgets.DateInput, Widget):
    input_classes = 'form-control form-control-1-8'


class DateTimeInput(widgets.DateTimeInput, Widget):
    input_classes = 'form-control form-control-1-4'


class TimeInput(widgets.TimeInput, Widget):
    input_classes = 'form-control form-control-1-8'


class Select(widgets.Select, Widget):
    pass


class NullBooleanSelect(widgets.NullBooleanSelect, Widget):
    input_classes = 'form-control form-control-1-4'
    default_choices = (
        ('1', _('Not set')),
        ('2', _('Yes')),
        ('3', _('No')),
    )

    def __init__(self, attrs=None):
        super(widgets.Select, self).__init__(attrs, self.default_choices)


class SelectMultiple(widgets.SelectMultiple, Select):
    pass


class FileInput(widgets.FileInput, Widget):
    input_classes = ''
    input_error_classes = ''


class ClearableFileInput(widgets.ClearableFileInput, FileInput):
    pass


class SelectDateWidget(MultiWidget):
    template_name = 'govuk_forms/widgets/split-date.html'
    select_widget = Select
    none_value = (0, _('Not set'))
    subwidget_group_classes = ('form-group form-group-day-select',
                               'form-group form-group-month-select',
                               'form-group form-group-year-select')
    subwidget_label_classes = ('form-label', 'form-label', 'form-label')  # or form-label-bold
    subwidget_labels = (_('Day'), _('Month'), _('Year'))

    def __init__(self, attrs=None, years=None, months=None, empty_label=None):
        this_year = datetime.date.today().year
        self.years = [(i, i) for i in years or range(this_year, this_year + 10)]
        self.months = [(month_value, month_name) for month_value, month_name in (months or MONTHS).items()]
        self.days = [(i, i) for i in range(1, 32)]

        if isinstance(empty_label, (list, tuple)):
            self.year_none_value = (0, empty_label[0])
            self.month_none_value = (0, empty_label[1])
            self.day_none_value = (0, empty_label[2])
        else:
            none_value = (0, empty_label) if empty_label is not None else self.none_value
            self.year_none_value = none_value
            self.month_none_value = none_value
            self.day_none_value = none_value

        date_widgets = (self.select_widget(attrs=attrs, choices=self.days),
                        self.select_widget(attrs=attrs, choices=self.months),
                        self.select_widget(attrs=attrs, choices=self.years))
        super().__init__(date_widgets, attrs=attrs)

    def get_context(self, name, value, attrs):
        iterators = zip(
            self.widgets,
            (self.days, self.months, self.years),
            (self.day_none_value, self.month_none_value, self.year_none_value)
        )
        for widget, choices, none_value in iterators:
            widget.is_required = self.is_required
            widget.choices = choices if self.is_required else [none_value] + choices
        return super().get_context(name, value, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]


widget_replacements = {
    widgets.TextInput: (TextInput, ()),
    widgets.NumberInput: (NumberInput, ()),
    widgets.EmailInput: (EmailInput, ()),
    widgets.URLInput: (URLInput, ()),
    widgets.PasswordInput: (PasswordInput, ('render_value',)),
    widgets.Textarea: (Textarea, ()),
    widgets.DateInput: (DateInput, ('format',)),
    widgets.DateTimeInput: (DateTimeInput, ('format',)),
    widgets.TimeInput: (TimeInput, ('format',)),
    widgets.Select: (Select, ('choices',)),
    widgets.SelectMultiple: (SelectMultiple, ('choices',)),
    widgets.NullBooleanSelect: (NullBooleanSelect, ()),
    widgets.CheckboxInput: (CheckboxInput, ('check_test',)),
    widgets.CheckboxSelectMultiple: (CheckboxSelectMultiple, ('choices',)),
    widgets.RadioSelect: (RadioSelect, ('choices',)),
    widgets.SplitDateTimeWidget: (SplitDateTimeWidget, ()),  # TODO: migrate formats
    widgets.FileInput: (FileInput, ()),
    widgets.ClearableFileInput: (ClearableFileInput, ()),
    widgets.SelectDateWidget: (SelectDateWidget, ('years', 'months')),  # TODO: migrate empty values
}


def replace_widget(widget, replacements):
    replacement = replacements.get(widget.__class__)
    if not replacement:
        return widget
    replacement_widget, widget_args = replacement
    replacement_widget = replacement_widget(attrs=widget.attrs, **{
        widget_arg: getattr(widget, widget_arg)
        for widget_arg in widget_args
    })
    replacement_widget.is_required = widget.is_required
    replacement_widget.is_localized = widget.is_localized
    return replacement_widget
