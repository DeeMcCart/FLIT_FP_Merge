from .models import Course
from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
#

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course  # Change to your course model
        course_code = forms.IntegerField()
        fields = ('course_code', 'version', 'title', 'subtitle', 'author', 'featured_image', 'effective_to', 'status' )  # Update fields as needed
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'