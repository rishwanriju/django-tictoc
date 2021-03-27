from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import custModel,tweet


class registerForm(UserCreationForm):
    class Meta:
        model = custModel
        fields =  ['email','password1','password2','username']
        widgets={
            'username':forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].required = False
       
    
class loginForm(forms.Form):
    email=forms.EmailField(required=True)
    password=forms.CharField(max_length=20, required=True,widget=forms.PasswordInput())

class tweetForm(forms.ModelForm):
    class Meta:
        model=tweet
        fields = ['content',"author"]
    
        widgets={
            "author":forms.HiddenInput()
        }



class updateForm(forms.ModelForm):
    class Meta:
        model=custModel
        fields = ["first_name","last_name","email","username"]
        widgets={
            "username":forms.HiddenInput()
        }
    
