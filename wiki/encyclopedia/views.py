import markdown2
import random

from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .forms import NewPageForm
from . import util
from markdown2 import Markdown

# define a global var for the markdown converter
markdowner = Markdown()


# Display the index or home page
def index(request):
    return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries()
                     }
                  )


# Display the content of a page title request
def entry(request, entry):  # based on the url it shows a md file
    try:
        content = markdown2.markdown(util.get_entry(entry))
    except entry.DoesNotExist:
        return HttpResponseNotFound("Page not found")
    # render the page while passing the content, and the capitalized title
    return render(request, "encyclopedia/entry.html", {
                         "entry": content,
                         "entryTitle": entry,
                         "title": entry.capitalize()
                        },
                  )


# Create a new page,if it exists add a warning to state
# that it is already in the database and allow edit.
def newPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        # Validate the form data
        if form.is_valid():
            # store the form date to title and content variable
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # If all validate or data converted to relevant python type
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                # save form data and redirect to right entry title
                util.save_entry(title, content)
                return HttpResponseRedirect(
                    reverse("encyclopedia:entry", kwargs={"entry": title})
                )
            else:
                return render(request, "encyclopedia/newPage.html", {
                    "form": form, "existing": True, "entry": title
                    },
                )
        else:
            return render(request, "encyclopedia/newPage.html", {
                    "form": form, "existing": False
                    }
            )
    else:
        return render(request, "encyclopedia/newPage.html", {
            "form": NewPageForm(), "existing": False
            },
        )


# Should it already exist create an edit function so changes can be made.
def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        # redirect is entry not found
        return render(request, "encyclopedia/index.html", {
                       "entryTitle": entry
                    }
            )
    else:
        # if it is edit form, display Edit form with initial data fields
        form = NewPageForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newPage.html", {
                "form": form,
                "edit": form.fields["edit"].initial,
                "entryTitle": form.fields["title"].initial,
            },
        )


# The random.choice() method returns a randomly
# selected element from a non-empty sequence
def randomEntryPage(request):
    # Retrieve the list of entries.
    entries = util.list_entries()
    # randomly select on of the entry using random.choice()
    randomEntry = random.choice(entries)
    return HttpResponseRedirect(
        reverse("encyclopedia:entry", kwargs={"entry": randomEntry})
    )


# search function
def search(request):
    # Let's get the search_string in url parameter
    searchString = request.GET.get("query")
    if util.get_entry(searchString) is not None:
        # If found let's reverse redirect with Kwargs Key-value pair.
        return HttpResponseRedirect(
            reverse("encyclopedia:entry", kwargs={"entry": searchString})
        )
    else:
        matchedEntries = []
        # Let's loop over the current list of entries
        for entry in util.list_entries():
            # if searchString matches one the entries
            # when both of them capitalized
            if searchString.upper() in entry.upper():
                # append the matching subString to the entry name
                matchedEntries.append(entry)
        # then render the index.html passing in the searchString
        # and a list matching subStringEntries titles
        return render(request, "encyclopedia/index.html", {
                "entries": matchedEntries,
                "search": True,
                "searchString": searchString
                },
        )
