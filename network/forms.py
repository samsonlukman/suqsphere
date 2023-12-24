from django import forms
from .models import LibraryDocument, Video, Group, User
import bleach

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class LibraryDocumentForm(forms.ModelForm):
    class Meta:
        model = LibraryDocument
        fields = ['title', 'file', 'category']  

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'file', 'category']  



class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmation = forms.CharField(widget=forms.PasswordInput)
    profile_pics = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirmation', 'profile_pics']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add placeholders for first_name, last_name, and username fields
        self.fields['first_name'].widget.attrs['placeholder'] = 'Max 15 characters'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Max 15 characters'
        self.fields['username'].widget.attrs['placeholder'] = ''

        # Set the email field as required
        self.fields['email'].required = True

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')[:15]  # Limit to 15 characters
        first_name = cleaned_data.get('first_name')[:15]  # Limit to 15 characters
        last_name = cleaned_data.get('last_name')[:15]  # Limit to 15 characters
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirmation = cleaned_data.get('confirmation')

        # Check if the username already exists in the database
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")

        # Check if the email already exists in the database
        a = User.objects.filter(email=email)
        if a.exists():
            raise forms.ValidationError("Email already registered.")
        

        if password and confirmation and password != confirmation:
            raise forms.ValidationError("Passwords must match.")

        # Update the cleaned_data with the truncated values
        self.cleaned_data['username'] = username
        self.cleaned_data['first_name'] = first_name
        self.cleaned_data['last_name'] = last_name

        return cleaned_data
