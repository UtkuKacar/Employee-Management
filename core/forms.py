from django import forms
from .models import Leave

class LeaveForm(forms.ModelForm):
    """Personel için izin tanımlama formu."""
    class Meta:
        model = Leave
        fields = ['employee', 'start_date', 'end_date', 'leave_type', 'is_approved']
        labels = {
            'employee': 'Personel',
            'start_date': 'Başlangıç Tarihi',
            'end_date': 'Bitiş Tarihi',
            'leave_type': 'İzin Türü',
            'is_approved': 'Onay Durumu',
        }
        help_texts = {
            'start_date': 'İzin başlangıç tarihini seçin.',
            'end_date': 'İzin bitiş tarihini seçin.',
            'leave_type': 'İzin türünü belirtin (örn. Yıllık İzin, Hastalık İzni).',
            'is_approved': 'Eğer onaylandıysa işaretleyin.',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.TextInput(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input', 'readonly': True}),  # readonly yapıldı
        }

    # Ek doğrulama (Validation)
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Tarih kontrolü: Başlangıç tarihi bitiş tarihinden büyük olamaz.
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'Bitiş tarihi, başlangıç tarihinden önce olamaz.')
