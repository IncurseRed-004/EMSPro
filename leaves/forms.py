from django import forms
from .models import LeaveRequest


class LeaveApplyForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'State the reason for taking leave'}),
        }


class LeaveReviewForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[('Approved', 'Approve Leave'), ('Rejected', 'Reject Leave')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = LeaveRequest
        fields = ['status', 'review_remark']
        widgets = {
            'review_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide feedback or reason for approval/rejection'}),
        }

