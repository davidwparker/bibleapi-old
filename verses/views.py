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
  verses = Verse().get_verses(version, book, chapter, verse, verse2)
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
  errors, notices = [], []
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
      common_words = ['an','and','as','is','it','of','or','the']
      terms = q.split()
      new_terms, common_words_used, args, kargs, books = [], [], [], [], []
      verses = None
      for term in terms:
        if term in common_words:
          common_words_used.append(term)
        else:
          new_terms.append(term)
      if len(common_words_used) > 0:
        notice = "The following words are too common and were not included in the search: "
        for word in common_words_used:
          notice += "'" + word + "' "
        notices.append(notice)
      if len(new_terms) == 0:
        errors.append("Enter a search term.")
      elif len(new_terms) == 1 and not new_terms[0].isnumeric() and len(new_terms[0]) > 2:
        books = Verse().get_book_names_from_abbr(v, new_terms[0])
        kargs.append(Q(verseText__icontains=new_terms[0]))
      else:
        book, chapter, verse, verse2 = None, None, None, None
        for i,term in enumerate(new_terms):
          if not term.isnumeric() and len(term) < 3:
            if term not in common_words_used:
              common_words_used.append(term)
              notices.append("The word '" + term + "' is too short and was not included in the search.")
          else:
            logging.debug(term)
            kargs.append(Q(verseText__icontains=term))
            if term.isnumeric():
              i_prev = i - 1
              i_next = i + 1
              if i_prev >= 0:
                prev_term = new_terms[i_prev]
                book_names = Verse().get_book_names_from_abbr(v, prev_term)
                if len(book_names) > 0:
                  chapter = new_terms[i]

              if book is None:
                try:
                  next_term = new_terms[i_next]
                  book_names = Verse().get_book_names_from_abbr(v, new_terms[i] + " " + next_term)
                  if len(book_names) > 0:
                    book = book_names[0]
                except:
                  pass

            else:
              book_names = Verse().get_book_names_from_abbr(v, term)
              result = re.match(r'^(?P<chapter>\d+)(:)?(?P<verse>\d+)?(\-)?(?P<verse2>\d+)?$', term)
              if result is not None:
                chapter = result.group('chapter')
                verse = result.group('verse')
                verse2 = result.group('verse2')
              if len(book_names) == 0 and result is None:
                args.append(Q(verseText__icontains=term))
              elif len(book_names) > 0:
                for book_name in book_names:
                  if book_name not in books:
                    books.append(book_name)

        if book is not None:
          args.append(Q(book__iexact=book))
        if chapter is not None:
          args.append(Q(chapter__iexact=chapter))
        if verse is not None and (verse2 is None or verse2 < verse):
          args.append(Q(verse__iexact=verse))
        elif verse2 is not None:
          args.append(Q(verse__in=range(int(verse),int(verse2)+1)))

        if chapter is not None and len(args) > 0 and len(books) > 0:
          verses = Verse.objects.filter(version__iexact=v).filter(Q(book__in=books)).filter(*args)

      if len(errors) == 0 and len(kargs) > 0:
        keyverses = Verse.objects.filter(version__iexact=v).filter(*kargs)
      
  return render_to_response('search_form.html',
    locals(), RequestContext(request))

#TODO: to-use
def versions(request):
  '''Returns a list of versions'''
  return ""

