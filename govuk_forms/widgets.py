from django import forms


class SplitDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (forms.NumberInput(attrs=attrs),
                   forms.NumberInput(attrs=attrs),
                   forms.NumberInput(attrs=attrs),)
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]


class SplitHiddenDateWidget(SplitDateWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        for widget in self.widgets:
            widget.input_type = 'hidden'
