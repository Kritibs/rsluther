from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms


class ContactForm(forms.Form):
    name = forms.EmailField(label='Email', max_length=60)
    message = forms.CharField(widget=forms.Textarea, label="How can we help you?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'name',
            'message',
            Submit('submit','Contact', css_class='btn-primary')
        )
