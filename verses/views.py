from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import list_detail

from verses.models import Verse

import array
import logging

def books(request, version):
  '''Returns a list of books for a given version'''
  Verse().version_exists_or_404(version)
  #get copyright info
  copyright = version
  return render_to_response('books.html', locals() , RequestContext(request))

def book_chapters(request, version):
  '''Returns a list of books and chapters for a given version'''
  Verse().version_exists_or_404(version)
  books = Verse().get_books(version)
  book_names = Verse().get_book_names(books)
  book_chapters = []
  logging.debug(book_names)
  for book in book_names:
    verses = Verse().get_chapters(version, book)
    chapters = Verse().get_chapter_numbers(verses)
    book_chapters.append({'book':book, 'chapters':chapters})
  copyright = version
  return render_to_response('book_chapters.html', locals(), RequestContext(request))

def chapters(request, version, book):
  '''Returns a list of chapters for a given version and book'''
  Verse().book_exists_or_404(version, book)
  verses = Verse().get_chapters(version, book)
  chapters = Verse().get_chapter_numbers(verses)
  return render_to_response('chapters.html', locals(), RequestContext(request))

def verses(request, version, book, chapter, verse, verse2):
  '''Returns a list of verses for a given version, book, chapter, and optional verses'''
  verses = Verse().get_verses_or_404(version, book, chapter, verse, verse2)
  if 'application/json' in request.META.get('HTTP_ACCEPT'):
    return HttpResponse(serializers.serialize("json", verses), mimetype='application/json')
  else:
    return list_detail.object_list(
      request,
      queryset = verses,
      template_name = 'verses.html',
      template_object_name = 'verses',
      extra_context = locals()
    )

def search(request):
  errors = []
  if 'q' in request.GET:
    q = request.GET['q']
    if not q:
      errors.append('Enter a search term.')
    elif len(q) > 20:
      errors.append('Please enter at most 20 characters.')
    else:
      verses = Verse.objects.filter(book__icontains=q)
      return render_to_response('search_form.html',
        {'errors':errors, 'verses':verses, 'q':q, 'request':request,}, RequestContext(request))
  return render_to_response('search_form.html',
    {'errors':errors, 'request':request,}, RequestContext(request))

#to-use
def versions(request):
  '''Returns a list of versions'''
  return ""

