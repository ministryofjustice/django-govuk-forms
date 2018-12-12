from django.forms import widgets
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
    (widgets.Select, 'govuk_forms/field-with-label.html'),
    ((widgets.MultiWidget, widgets.ChoiceWidget), 'govuk_forms/field-as-fieldset.html'),
    (widgets.CheckboxInput, 'govuk_forms/field-without-label.html'),
    (widgets.Widget, 'govuk_forms/field-with-label.html'),
)


class Widget(widgets.Widget):
    group_template_name = 'govuk_forms/field-with-label.html'
    input_classes = 'govuk-input'
    input_error_classes = 'govuk-input--error'

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        css_classes = self.input_classes() if callable(self.input_classes) else self.input_classes
        attrs['class'] = ('%s %s' % (attrs.get('class', ''), css_classes)).strip()
        return attrs


class MultiWidget(widgets.MultiWidget, Widget):
    group_template_name = 'govuk_forms/field-as-fieldset.html'
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


class CheckboxInput(widgets.CheckboxInput, Widget):
    template_name = 'govuk_forms/widgets/checkbox.html'
    group_template_name = 'govuk_forms/field-without-label.html'
    input_classes = 'govuk-checkboxes__input'
    input_error_classes = 'govuk-checkboxes__input--error'

    conditionally_revealed_module = 'checkboxes'
    conditional_panel_classes = 'govuk-checkboxes__conditional'
    conditional_panel_hidden_classes = 'govuk-checkboxes__conditional govuk-checkboxes__conditional--hidden'

    inherit_label_from_field = True
    label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionally_revealed = {}

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.label:
            context['widget']['label'] = self.label

        conditionally_revealed = self.conditionally_revealed.get(True)
        context['conditionally_revealed'] = conditionally_revealed
        if conditionally_revealed:
            context['conditionally_revealed_module'] = self.conditionally_revealed_module
            revealed_target = '%s-conditional' % conditionally_revealed['bound_field'].auto_id
            context['widget']['attrs']['data-aria-controls'] = revealed_target
            if value:
                context['conditional_panel_classes'] = self.conditional_panel_classes
            else:
                context['conditional_panel_classes'] = self.conditional_panel_hidden_classes

        return context


class ChoiceWidget(widgets.ChoiceWidget, Widget):
    template_name = 'govuk_forms/widgets/multiple-select.html'
    option_template_name = 'govuk_forms/widgets/multiple-select-option.html'
    group_template_name = 'govuk_forms/field-as-fieldset.html'

    choices_wrapper_classes = ''
    option_group_legend_classes = 'govuk-fieldset__legend'
    option_wrapper_classes = ''
    option_label_classes = ''

    separate_last_option = False
    divider_classes = ''
    last_option_divider = _('or')

    conditionally_revealed_module = ''
    conditional_panel_classes = ''
    conditional_panel_hidden_classes = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionally_revealed = {}

    @property
    def is_flat_list(self):
        return not any(isinstance(choice, (tuple, list)) for name, choice in self.choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['choices_wrapper_classes'] = self.choices_wrapper_classes
        context.update(
            is_flat_list=self.is_flat_list,
            separate_last_option=self.separate_last_option,
            divider_classes=self.divider_classes,
            last_option_divider=self.last_option_divider,
            option_group_legend_classes=self.option_group_legend_classes,
            conditionally_revealed_module=self.conditionally_revealed and self.conditionally_revealed_module,
        )
        return context

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['option_wrapper_classes'] = self.option_wrapper_classes
        option['option_label_classes'] = self.option_label_classes
        if self.conditionally_revealed:
            conditionally_revealed = self.conditionally_revealed.get(value)
            option['conditionally_revealed'] = conditionally_revealed
            if conditionally_revealed:
                revealed_target = '%s-conditional' % conditionally_revealed['bound_field'].auto_id
                option['attrs']['data-aria-controls'] = revealed_target
                if selected:
                    option['conditional_panel_classes'] = self.conditional_panel_classes
                else:
                    option['conditional_panel_classes'] = self.conditional_panel_hidden_classes
        return option


class CheckboxSelectMultiple(ChoiceWidget, widgets.CheckboxSelectMultiple):
    choices_wrapper_classes = 'govuk-checkboxes'
    option_wrapper_classes = 'govuk-checkboxes__item'
    option_label_classes = 'govuk-label govuk-checkboxes__label'
    input_classes = 'govuk-checkboxes__input'
    input_error_classes = 'govuk-checkboxes__input--error'
    conditionally_revealed_module = 'checkboxes'
    conditional_panel_classes = 'govuk-checkboxes__conditional'
    conditional_panel_hidden_classes = 'govuk-checkboxes__conditional govuk-checkboxes__conditional--hidden'


class InlineCheckboxSelectMultiple(CheckboxSelectMultiple):
    choices_wrapper_classes = 'govuk-checkboxes govuk-checkboxes--inline'


class SeparatedCheckboxSelectMultiple(CheckboxSelectMultiple):
    separate_last_option = True
    divider_classes = 'govuk-checkboxes__divider'


class RadioSelect(ChoiceWidget, widgets.RadioSelect):
    choices_wrapper_classes = 'govuk-radios'
    option_wrapper_classes = 'govuk-radios__item'
    option_label_classes = 'govuk-label govuk-radios__label'
    input_classes = 'govuk-radios__input'
    input_error_classes = 'govuk-radios__input--error'
    conditionally_revealed_module = 'radios'
    conditional_panel_classes = 'govuk-radios__conditional'
    conditional_panel_hidden_classes = 'govuk-radios__conditional govuk-radios__conditional--hidden'


class InlineRadioSelect(RadioSelect):
    choices_wrapper_classes = 'govuk-radios govuk-radios--inline'


class SeparatedRadioSelect(RadioSelect):
    separate_last_option = True
    divider_classes = 'govuk-radios__divider'


class TextInput(widgets.TextInput, Widget):
    pass


class NumberInput(widgets.NumberInput, Widget):
    input_classes = 'govuk-input govuk-input--width-5'


class EmailInput(widgets.EmailInput, Widget):
    pass


class URLInput(widgets.URLInput, Widget):
    input_classes = 'govuk-input govuk-!-width-full'


class PasswordInput(widgets.PasswordInput, Widget):
    input_classes = 'govuk-input govuk-input--width-20'


class Textarea(widgets.Textarea, Widget):
    input_classes = 'govuk-textarea'
    input_error_classes = 'govuk-textarea--error'

    def __init__(self, attrs=None):
        default_attrs = {'cols': '60', 'rows': '5'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class DateInput(widgets.DateInput, Widget):
    input_classes = 'govuk-input govuk-input--width-10'


class DateTimeInput(widgets.DateTimeInput, Widget):
    input_classes = 'govuk-input govuk-input--width-10'


class TimeInput(widgets.TimeInput, Widget):
    input_classes = 'govuk-input govuk-input--width-10'


class Select(widgets.Select, Widget):
    group_template_name = 'govuk_forms/field-with-label.html'
    input_classes = 'govuk-select'
    input_error_classes = 'govuk-select--error'


class NullBooleanSelect(widgets.NullBooleanSelect, Widget):
    input_classes = 'govuk-select govuk-input--width-5'
    input_error_classes = 'govuk-select--error'
    default_choices = (
        ('1', _('Not set')),
        ('2', _('Yes')),
        ('3', _('No')),
    )

    def __init__(self, attrs=None):
        super(widgets.Select, self).__init__(attrs=attrs, choices=self.default_choices)


class SelectMultiple(widgets.SelectMultiple, Select):
    input_classes = 'govuk-select-multiple'
    input_error_classes = 'govuk-select-multiple--error'


class FileInput(widgets.FileInput, Widget):
    input_classes = 'govuk-file-upload'
    input_error_classes = 'govuk-file-upload--error'


class ClearableFileInput(widgets.ClearableFileInput, FileInput):
    # TODO: this widget is not complete
    template_name = 'govuk_forms/widgets/clearable-file-input.html'
    initial_text = _('Keep uploaded file')
    clear_checkbox_label = _('Remove uploaded file')
    input_text = _('Upload a new file')


class SplitDateWidget(MultiWidget):
    template_name = 'govuk_forms/widgets/split-date.html'
    input_classes = ''
    input_error_classes = ''
    subwidgets = [NumberInput, NumberInput, NumberInput]
    subwidget_group_classes = ('govuk-form-group govuk-form-group--day',
                               'govuk-form-group govuk-form-group--month',
                               'govuk-form-group govuk-form-group--year')
    subwidget_label_classes = ('govuk-label govuk-date-input__label',
                               'govuk-label govuk-date-input__label',
                               'govuk-label govuk-date-input__label')
    subwidget_labels = (_('Day'), _('Month'), _('Year'))
    subwidget_input_classes = ('govuk-input govuk-date-input__input govuk-input--width-2',
                               'govuk-input govuk-date-input__input govuk-input--width-2',
                               'govuk-input govuk-date-input__input govuk-input--width-4')

    def __init__(self, attrs=None):
        options = zip(self.subwidgets, self.subwidget_input_classes)
        date_widgets = []
        for subwidget, input_classes in options:
            subwidget = subwidget(attrs=attrs)
            subwidget.input_classes = input_classes
            date_widgets.append(subwidget)
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
    input_classes = ''
    input_error_classes = ''
    subwidgets = [DateInput, TimeInput]
    subwidget_group_classes = ('govuk-form-group govuk-form-group--date',
                               'govuk-form-group govuk-form-group--time')
    subwidget_label_classes = ('govuk-label govuk-date-input__label',
                               'govuk-label govuk-date-input__label')
    subwidget_labels = (_('Date'), _('Time'))

    def __init__(self, attrs=None):
        date_widgets = (self.subwidgets[0](attrs=attrs),
                        self.subwidgets[1](attrs=attrs),)
        super(MultiWidget, self).__init__(date_widgets, attrs)


class SplitHiddenDateTimeWidget(SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for widget in self.widgets:
            widget.input_type = 'hidden'


class SelectDateWidget(widgets.SelectDateWidget, Widget):
    template_name = 'govuk_forms/widgets/split-date.html'
    input_classes = ''
    input_error_classes = ''
    none_value = ('', _('Not set'))
    select_widget = Select
    subwidget_group_classes = ('govuk-form-group govuk-form-group--day-select',
                               'govuk-form-group govuk-form-group--month-select',
                               'govuk-form-group govuk-form-group--year-select')
    subwidget_label_classes = ('govuk-label govuk-date-input__label',
                               'govuk-label govuk-date-input__label',
                               'govuk-label govuk-date-input__label')
    subwidget_labels = (_('Day'), _('Month'), _('Year'))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        options = zip(
            context['widget']['subwidgets'],
            self.subwidget_group_classes,
            self.subwidget_label_classes,
            self.subwidget_labels,
        )
        for subwidget, group_classes, label_classes, label in options:
            subwidget['group_classes'] = group_classes
            subwidget['label_classes'] = label_classes
            subwidget['label'] = label
        return context


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
    widgets.SplitDateTimeWidget: (SplitDateTimeWidget, ()),
    widgets.FileInput: (FileInput, ()),
    widgets.ClearableFileInput: (ClearableFileInput, ()),
    widgets.SelectDateWidget: (SelectDateWidget, ('years', 'months')),
}


def replace_widget(widget, replacements):
    replacement = replacements.get(widget.__class__)
    if not replacement:
        return widget
    replacement_widget, widget_attrs = replacement
    replacement_widget = replacement_widget(attrs=widget.attrs, **{
        widget_attr: getattr(widget, widget_attr)
        for widget_attr in widget_attrs
    })
    replacement_widget.is_required = widget.is_required
    replacement_widget.is_localized = widget.is_localized
    return replacement_widget
