from django import forms

#Create a class for a new entry form for adding new content to the entries file in markdown.
class NewPageForm(forms.Form):
    title = forms.CharField(label="Title",widget =forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 6}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(),required=False)



