import datetime

from django import forms
from datetimewidget.widgets import DateWidget
from django.forms.widgets import TextInput, CheckboxInput, Textarea

from .models import PlaylistEntry, Playlist, Show


class SummaryReportForm(forms.Form):
    startDate = forms.DateField(label='Start Date', widget=DateWidget(usel10n=True, bootstrap_version=3))
    endDate = forms.DateField(label='End Date', widget=DateWidget(usel10n=True, bootstrap_version=3))
    reportFormat = forms.ChoiceField(label="Report Format", choices = (('top20', 'Top 20+1'),('apra', 'APRA')))

    def clean(self):
        cleaned_data = super(SummaryReportForm, self).clean()
        if cleaned_data.get("startDate") > cleaned_data.get("endDate"):
            self.add_error('startDate', "")
            self.add_error('endDate', '')
            raise forms.ValidationError("End date cannot be before Start Date!")
