import secrets
from collections import Counter

import numpy as np
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from gas.models import targets, class_data, classes, class_pr, first_show, searcher
from gas.settings import USING_SOM, SHOWING


def prepare_data(request, data, find):
    """
    Generate data used in template (results of search) and send the data to the index.html template.

    Args:
        request (HttpRequest): The HTTP request.
        data (list): The list of search results.
        find (int): The index of currently searching image.

    Returns:
        HttpResponse: The HTTP response.
    """
    template = loader.get_template('index.html')

    # get classes of current shown result
    data_to_display = {str(i): ([] if i not in class_data else class_data[i]) for i in data}
    # get top classes contains in result
    top_classes = [word for word, word_count in
                   Counter(np.concatenate([a for a in data_to_display.values()], axis=None)).most_common(5) if
                   word_count > 5]

    sending_data = {
        'list_photo': data_to_display,
        'percent': class_pr,
        'classes': ','.join(classes),
        'top_classes': top_classes[::-1],
        'find_id': str(find)
    }

    return HttpResponse(template.render(sending_data, request))


def search(request):
    """
    Performs a search query and send the result to the template.

    Args:
        request (HttpRequest): The HTTP request containing information about the current request.

    Returns:
        Union[HttpResponse, HttpResponseRedirect]: The HTTP response.
    """
    if not request.session.get('session_id'):
        return render(request, 'index.html')

    # load index of currently searching image from cookies
    found = int(request.COOKIES.get('index')) if request.COOKIES.get('index') is not None else 0
    if found >= len(targets):  # control of end
        return redirect('/end')
    data = first_show if USING_SOM else np.arange(1, SHOWING + 1)

    if request.GET.get('query'):
        data = searcher.text_search(request.GET['query'], request.session['session_id'], found,
                                    request.COOKIES.get('activity')[:-1])
    else:
        # reset save search if user use any other method than text search
        searcher.reset_last(request.session['session_id'])
        if request.GET.get('id'):
            data = searcher.image_search(request.GET['id'], found, request.session['session_id'])

    return prepare_data(request, data, targets[found])


def start(request):
    """
    Sets the session id and renders the start.html template (welcome page).

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response containing the data to be displayed in the template.
    """
    # "login" - setting session id
    request.session['session_id'] = secrets.token_urlsafe(6)
    searcher.reset_last(request.session['session_id'])
    return render(request, 'start.html')


def end(request):
    """
    Renders the end.html template (final page).

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response containing the data to be displayed in the template.
    """
    return render(request, 'end.html')
