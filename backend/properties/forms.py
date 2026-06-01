from django import forms
from .models import Property, PropertyImage, ContactMessage

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title','description','price','location','property_type','listing_type',
                  'bedrooms','bathrooms','area_sqft','amenities','furnished','is_featured','status','category']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs.update({'class':'form-check-input'})
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs.update({'class':'form-select'})
            else:
                f.widget.attrs.update({'class':'form-control'})

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image','caption']
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        for f in self.fields.values():
            f.widget.attrs.update({'class':'form-control'})

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name','email','phone','message']
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        placeholders = {
            'name': 'Your name',
            'email': 'Email address',
            'phone': 'Phone number',
            'message': "I'm interested in this property.",
        }
        for f in self.fields.values():
            f.widget.attrs.update({'class':'form-control'})
        for name, placeholder in placeholders.items():
            self.fields[name].widget.attrs.update({'placeholder': placeholder})
