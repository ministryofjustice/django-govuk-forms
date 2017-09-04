from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
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
    field_group_panel_classes = 'panel panel-border-narrow js-hidden'
    field_label_classes = 'form-label'  # or form-label-bold
    field_help_classes = 'form-hint'

    error_summary_title = _('There are problems in the form')
    error_summary_template_name = 'govuk_forms/error-summary.html'

    submit_button_label = _('Submit')
    submit_button_template_name = 'govuk_forms/submit-button.html'

    reveal_conditionally = {}
    fieldsets = ()
    fieldset_template_name = 'govuk_forms/fieldset.html'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

        if self.auto_replace_widgets:
            widget_replacements = govuk_widgets.widget_replacements
            if hasattr(self, 'widget_replacements'):
                widget_replacements = widget_replacements.copy().update(self.widget_replacements)
            for field in self.fields.values():
                field.widget = govuk_widgets.replace_widget(field.widget, widget_replacements)

        self.conditionally_revealed = {}
        for target_fields in self.reveal_conditionally.values():
            for target_field in target_fields.values():
                field = self.fields[target_field]
                self.conditionally_revealed[target_field] = {
                    'required': field.required,
                }
                field.required = False

    def __str__(self):
        return self.as_div()

    def clean(self):
        super().clean()
        for choice_field_name, details in self.reveal_conditionally.items():
            chosen_value = self.cleaned_data.get(choice_field_name, object())
            choice_field = self.fields[choice_field_name]
            multi_choice = isinstance(choice_field, forms.MultipleChoiceField)
            if not multi_choice:
                chosen_value = [chosen_value]
            for chosen_value in chosen_value:
                target_field_name = details.get(chosen_value)
                if not target_field_name:
                    continue
                conditionally_revealed = self.conditionally_revealed.get(target_field_name)
                if not conditionally_revealed.get('required'):
                    continue
                target_value = self.cleaned_data[target_field_name]
                target_field = self.fields[target_field_name]
                if target_value in target_field.empty_values:
                    self.add_error(target_field_name, ValidationError(target_field.error_messages['required'],
                                                                      code='required'))
        return self.cleaned_data

    def get_group_template_name(self, widget):
        for widget_classes, template_name in self.group_template_names:
            if isinstance(widget, widget_classes):
                return template_name
        raise ValueError('Cannot determine template name for widget %r' % widget)

    def as_div(self):
        rows = []
        included_fields = set()
        for field_name, conditionally_revealed in self.conditionally_revealed.items():
            included_fields.add(field_name)
            conditionally_revealed['html'] = self.render_field(field_name, self.fields[field_name], in_panel=True)
        for legend, field_names in self.fieldsets:
            included_fields.update(field_names)
            context = {
                'legend': legend,
                'contents': format_html_join('\n\n', '{}', (
                    (self.render_field(field_name, self.fields[field_name]),)
                    for field_name in field_names
                )),
            }
            rows.append((mark_safe(self.renderer.render(self.fieldset_template_name, context)),))
        rows.extend(
            (self.render_field(name, field),)
            for name, field in self.fields.items()
            if name not in included_fields
        )
        return format_html_join('\n\n', '{}', rows)

    def render_field(self, name, field, in_panel=False):
        bound_field = self[name]
        if bound_field.is_hidden:
            return bound_field

        widget = field.widget
        if hasattr(widget, 'conditionally_revealed'):
            widget.conditionally_revealed = {
                value: {
                    'bound_field': self[target_field],
                    'html': self.conditionally_revealed[target_field]['html'],
                }
                for value, target_field in self.reveal_conditionally.get(name, {}).items()
            }
        errors = [conditional_escape(error) for error in bound_field.errors]
        group_classes = self.field_group_panel_classes if in_panel else self.field_group_classes
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
        return mark_safe(self.renderer.render(group_template_name, field_context))

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
