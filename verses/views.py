from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import list_detail

from verses.models import Verse

import array
import logging

def book_chapters(request, version):
  '''Returns a list of books and chapters for a given version'''
  Verse().version_exists_or_404(version)
  book_chapters = Verse().get_book_chapters(version)
  copyright = version
  return render_to_response('book_chapters.html', locals(), RequestContext(request))

def chapters(request, version, book):
  '''Returns a list of chapters for a given version and book'''
  Verse().book_exists_or_404(version, book)
  chapters = Verse().get_chapter_numbers(version, book)
  if 'application/json' in request.META.get('HTTP_ACCEPT'):
    json = "{'book':'"+book+"','chapters':["+"".join(str(chapter)+"," for chapter in chapters)+"]}"
    return HttpResponse(json, mimetype='application/json')
  else:
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
  import re
  errors = []
  if 'q' in request.GET:
    q = request.GET['q']
    v = request.GET['v']
    if not q or q.isspace():
      errors.append('Enter a search term.')
    elif not Verse().version_exists(v):
      errors.append('Version does not exists.')
    else:
      #parse q
        #1) filter and check to make sure isn't a common word:
        # of, the, is, have, had, he, she, it, and, or, 
        #2) check to see if it's a book in the bible, if so, then 
        # have a second section on the screen to click to that book
      has_numbers = False
      common_words = ['and','is','it','or','of','the']
      common_words_set = set(common_words)
      terms = q.split()
      terms_set = set(terms)
      common_words_used = terms_set & common_words_set
      new_terms = terms_set - common_words_set
      logging.debug("common used: " + str(common_words_used))
      logging.debug("new terms:   " + str(new_terms))
      for term in new_terms:
        if term.isnumeric():
          has_numbers = True
      if len(common_words_used) > 0:
        error = "The following words are too common and were not included in the search: "
        for word in common_words_used:
          error += "'" + word + "' "
        errors.append(error)
      #keyword search only
      if len(new_terms) == 1:
        verses = Verse.objects.filter(version__iexact=v, verseText__icontains=list(new_terms)[0])
      else:
        if has_numbers:
          #if all terms are numbers, fail
  #        if terms[0].isnumeric() & terms[1].isnumeric():
          logging.debug("TODO: FAIL")
          errors.append('You must supply more than just numbers.')
          verses = None
        else:
          books = []
          args = []
          for term in new_terms:
            book_names = Verse().get_book_names_from_abbr(v, term)
            if len(book_names) > 0:
              logging.debug(book_names)
              for book in book_names:
                books.append(book)
            else:
              #need to check for : here too
              logging.debug('just a term: ' + term)
              args.append(Q(verseText__icontains=term))
          if len(books) == 0:
            logging.debug('here')
            #keyword keyword search
            verses = Verse.objects.filter(version__iexact=v).filter(*args)
          else:
            #book keyword search
            logging.debug('there')
            logging.debug(books)
            verses = Verse.objects.filter(version__iexact=v).filter(Q(book__in=books)).filter(*args)
            logging.debug(len(verses))
      if len(terms) == 4:
        logging.debug("four")
      else:
        logging.debug(terms)
        for term in terms:
          logging.debug("term " + term)
          if len(term) > 2:
            book_names = Verse().get_book_names_from_abbr(v, term)
            if book_names:
              logging.debug(book_names[0])
              isBook = Verse().book_exists(v, book_names[0])
              if isBook:
                book = book_names[0]
              else:
                result = re.match('(\d+)?(:)?(\d+)?(\-)?(\d+)?', term)
                if result is not None:
                  logging.debug(result.group(0))
                  logging.debug(result.group(1))
                  logging.debug(result.group(2))
                  logging.debug(result.group(3))
                  logging.debug(result.group(4))
                  logging.debug(result.group(5))
                  chapter = result.group(1)
                  verse   = result.group(3)
                  verse2  = result.group(5)
          else:
            result = re.match('(\d+)?(:)?(\d+)?(\-)?(\d+)?', term)
            if result is not None:
              logging.debug(result.group(0))
              logging.debug(result.group(1))
              logging.debug(result.group(2))
              logging.debug(result.group(3))
              logging.debug(result.group(4))
              logging.debug(result.group(5))
              chapter = result.group(1)
              verse   = result.group(3)
              verse2  = result.group(5)

      if verses is None:
        logging.debug('last minute search')
        verses = Verse().get_verses_or_404(v, book, chapter, verse, verse2)
      return render_to_response('search_form.html',
        locals(), RequestContext(request))
  return render_to_response('search_form.html',
    {'errors':errors, 'request':request,}, RequestContext(request))

#to-use
def versions(request):
  '''Returns a list of versions'''
  return ""

