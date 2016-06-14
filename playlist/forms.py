import datetime

from django import forms
from datetimewidget.widgets import DateWidget
from django.forms.widgets import TextInput, CheckboxInput, Textarea

from .models import PlaylistEntry, Playlist, Show


class ShortDurationField(forms.DurationField):
    def prepare_value(self, value):
        if isinstance(value, datetime.timedelta):
            seconds = value.total_seconds()

            hours = int(seconds // (60 * 60))
            minutes = int((seconds - hours * 60 * 60) // 60)
            second = int(seconds % 60)
            if hours > 0:
                return '{:01d}:{:02d}:{:02d}'.format(hours, minutes, second)

            return '{:01d}:{:02d}'.format(minutes, second)
        else:
            # In case something went wrong
            return super(forms.DurationField, self).prepare_value(value)

    def clean(self, value):
        if value is None or value == '':
            return '0'
        return super(forms.DurationField, self).clean(value)


class NewPlaylistForm(forms.ModelForm):
    show = forms.ModelChoiceField(Show.objects.order_by('name'), required=True)

    class Meta:
        model = Playlist
        fields = ['show', 'host', 'date', 'notes']
        widgets = {
            'date': DateWidget(usel10n=True, bootstrap_version=3),
            'notes': Textarea(
                attrs={'placeholder': 'Show notes, interview details, etc.'}
            )
        }


class PlaylistEntryForm(forms.ModelForm):
    duration = ShortDurationField(
        widget=TextInput(attrs={'placeholder': 'mm:ss', 'class': "form-control input-sm", 'style': 'width: 60px;'}), )
    error_css_class = 'has-error'

    class Meta:
        model = PlaylistEntry
        exclude = {'playlist', 'catalogueEntry'}
        widgets = {
            'artist': TextInput(attrs={'placeholder': 'Artist', 'class': "form-control input-sm typeahead-artist"}),
            'title': TextInput(attrs={'placeholder': 'Track', 'class': "form-control input-sm typeahead-track"}),
            'album': TextInput(attrs={'placeholder': 'Album', 'class': "form-control input-sm"}),
            'local': CheckboxInput(attrs={'class': "local_check", }),
            'australian': CheckboxInput(attrs={'class': "australian_check", }),
            'female': CheckboxInput(attrs={'class': "female_check", }),
        }


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
