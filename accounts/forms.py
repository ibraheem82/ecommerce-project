from django import forms
from . models import Account, UserProfile

# ===> using django modelForm
class RegistrationForm(forms.ModelForm):
    # ===> how we want our password input fields to be
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class' : 'form-control'
    }))
   
   
   
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
   
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
        
            # ===> we want to checking if the password the user are entering match or not.
    def clean(self):
        # ===> the 'super' class will allow you to change the way it is saving or change the way the class is been saved
        # ===> we are modifying the super class.
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!❗❌"
            )
        
        
        
        # ===> we are modifying our class so that we can be able to edit the boostrap of our forms
        # ===> we are overiding the functionality of the form
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # ===> we are setting the placeholder for each fields
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        # ===> we are looping through all the fields we have
        for field in self.fields:
            # ===> and this will assign all the attribute class to the fields we have looped through earlier
            self.fields[field].widget.attrs['class'] = 'form-control'



class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')
        
        # ===> we are modifying our class so that we can be able to edit the boostrap of our forms
        # ===> we are overiding the functionality of the form
        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            # ===> we are looping through all the fields we have
            for field in self.fields:
                # ===> and this will assign all the attribute class to the fields we have looped through earlier
                self.fields[field].widget.attrs['class'] = 'form-control'
            
        
        
class UserProfileForm(forms.ModelForm):
    # this is use to get rid of the image type and name in the edit form, getting rid of the path
    profile_picture = forms.ImageField(required=False, error_messages= {'invalid': ("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')
        # ===> we are modifying our class so that we can be able to edit the boostrap of our forms
        # ===> we are overiding the functionality of the form
        def __init__(self, *args, **kwargs):
            super(UserProfileForm, self).__init__(*args, **kwargs)
            # ===> we are looping through all the fields we have
            for field in self.fields:
                # ===> and this will assign all the attribute class to the fields we have looped through earlier
                self.fields[field].widget.attrs['class'] = 'form-control'
            
            
