import markdown2
import secrets

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django import forms
from . forms import NewPageForm

from . import util
from markdown2 import Markdown

# define a global var for the markdown converter
markdowner = Markdown()



# Display the index or home page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Display the content of a page title request
def entry(request, entry): #based on the url it shows a md file
    try:
        content = markdown2.markdown(util.get_entry(entry))
    except:          
        return HttpResponseNotFound("Page not found")
    # render the page while passing the content, the capitalized title
    return render(request, "encyclopedia/entry.html", {
            "entry": content, 
            "entryTitle": entry,
            "title": entry.capitalize()
        })

# #Create a new page, if it exists add a warning to state that it is already in the database and allow edit.
def newPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title) is None or form.cleaned_data["edit"] is True:
                util.save_entry(title, content)
                return HttpResponseRedirect(
                    reverse("encyclopedia:entry", kwargs={"entry": title})
                )
            else:
                return render(
                    request,
                    "encyclopedia/newPage.html",
                    {"form": form, "existing": True, "entry": title},
                )
        else:
            return render(
                request, "encyclopedia/newPage.html", {"form": form, "existing": False}
            )
    else:
        return render(
            request,
            "encyclopedia/newPage.html",
            {"form": NewPageForm(), "existing": False},
        )

# Should it already exist create an edit function so changes can be made.
def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonEntry.html", {"entryTitle": entry})
    else:
        form = NewPageForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(
            request,
            "encyclopedia/newPage.html",
            {
                "form": form,
                "edit": form.fields["edit"].initial,
                "entryTitle": form.fields["title"].initial,
            },
        )

#Using the Python secrets.choice(entries) method to Retrieve  a random entry page.
def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'entry': randomEntry}))

# Search for an entry title in encyclopedia
def search(request):   
    #Let's get the search_string in url parameter
    searchString = request.GET.get('query')    
    if(util.get_entry(searchString) is not None):
        # If found let's reverse redirect with Kwargs Key-value.
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'entry': searchString }))    
    else:
        subStringEntries = []
        #Let's loop over the current list of entries
        for entry in util.list_entries(): 
            #if searchString matches one the entries when both of them capitalized 
            if searchString.upper() in entry.upper(): 
                    #append the matching subString to the entry name
                    subStringEntries.append(entry)
        #then render the index.html passing in the searchString and a list matching subStringEntries titles
        return render(request, "encyclopedia/index.html", {
        "entries": subStringEntries,
        "search": True,
        "searchString": searchString
    })
