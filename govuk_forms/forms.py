from collections import OrderedDict

from django import forms
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from govuk_forms import widgets as govuk_widgets


class GOVUKForm(forms.Form):
    error_css_class = 'form-group-error'
    required_css_class = 'form-group-required'  # no default styling

    auto_replace_widgets = False
    group_template_names = govuk_widgets.group_template_names

    field_group_classes = 'form-group'
    field_label_classes = 'form-label'  # or form-label-bold
    field_help_classes = 'form-hint'

    error_summary_title = _('There are problems in the form')
    error_summary_template_name = 'govuk_forms/error-summary.html'

    submit_button_label = _('Submit')
    submit_button_template_name = 'govuk_forms/submit-button.html'

    def __init__(self, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(**kwargs)
        if self.auto_replace_widgets:
            widget_replacements = govuk_widgets.widget_replacements
            if hasattr(self, 'widget_replacements'):
                widget_replacements = widget_replacements.copy().update(self.widget_replacements)
            for field in self.fields.values():
                field.widget = govuk_widgets.replace_widget(field.widget, widget_replacements)

    def __str__(self):
        return self.as_fieldset()

    def get_group_template_name(self, widget):
        for widget_classes, template_name in self.group_template_names:
            if isinstance(widget, widget_classes):
                return template_name
        raise ValueError('Cannot determine template name for widget %r' % widget)

    def as_div(self):
        rows = []

        for name, field in self.fields.items():
            bound_field = self[name]
            if bound_field.is_hidden:
                rows.append(bound_field)
                continue

            widget = field.widget
            errors = [conditional_escape(error) for error in bound_field.errors]
            group_classes = self.field_group_classes
            if hasattr(widget, 'field_group_classes'):
                group_classes = '%s %s' % (group_classes, widget.field_group_classes)
            group_classes = bound_field.css_classes(group_classes)
            label_classes = self.field_label_classes
            help_classes = self.field_help_classes
            if bound_field.label:
                label = conditional_escape(force_text(bound_field.label))
            else:
                label = ''
            if getattr(widget, 'inherit_label_from_field', False):
                widget.label = label
            if field.help_text:
                help_text = force_text(field.help_text)
            else:
                help_text = ''

            if errors:
                widget_classes = getattr(widget, 'input_error_classes', 'form-control-error')
            else:
                widget_classes = ''
            widget_attrs = {
                'class': widget_classes,
            }
            rendered_field = bound_field.as_widget(attrs=widget_attrs)
            if field.show_hidden_initial:
                rendered_field += bound_field.as_hidden(only_initial=True)

            field_context = {
                'bound_field': bound_field,
                'rendered_field': rendered_field,
                'errors': errors,
                'group_classes': group_classes.strip(),
                'label_classes': label_classes.strip(),
                'help_classes': help_classes.strip(),
                'label': label,
                'help_text': help_text,
            }
            group_template_name = self.get_group_template_name(widget)
            rows.append(mark_safe(self.renderer.render(group_template_name, field_context)))

        return format_html_join('\n\n', '{}', ((row,) for row in rows))

    def error_summary(self, error_summary_title=None):
        errors = self.errors
        if not errors:
            return ''

        non_field_errors = self.non_field_errors()
        field_errors = OrderedDict(
            (field, errors[field.name])
            for field in self
            if field.name in self.errors
        )
        context = {
            'error_summary_title': error_summary_title or self.error_summary_title,
            'random_string': get_random_string(4),
            'errors': errors,  # does not preserve field order
            'non_field_errors': non_field_errors,
            'field_errors': field_errors,
        }
        return mark_safe(self.renderer.render(self.error_summary_template_name, context))

    def submit_button(self, label=None):
        context = {'label': label or self.submit_button_label}
        return mark_safe(self.renderer.render(self.submit_button_template_name, context))
