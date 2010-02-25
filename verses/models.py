from django.db import models
from django.http import Http404

class Verse(models.Model):
  version = models.CharField(max_length=100)
  book = models.CharField(max_length=100)
  chapter = models.IntegerField()
  verse = models.IntegerField()
  verseText = models.TextField('text')
  
  class Meta:
    db_table = 'verses'
    ordering = ('chapter','verse')
  
  #django methods  
  def __unicode__(self):
    return self.version + " " + self.book + " " + unicode(self.chapter) + ":" + unicode(self.verse)

  #class methods here down
  #
  # existence
  #
  def book_exists(self, version, book):
    '''Returns whether a book exists'''
    return Verse().get_chapters(version, book).exists()

  def book_exists_or_404(self, version, book):
    '''Raises Http404 if book does not exist'''
    if not Verse().book_exists(version, book):
      raise Http404

  def version_exists(self, version):
    '''Returns whether a version exists'''
    return Verse.objects.filter(version__iexact=version).exists()

  def version_exists_or_404(self, version):
    '''Raises Http404 if version does not exist'''
    if not Verse().version_exists(version):
      raise Http404

  #
  # filters/lists of objects
  #
  def get_books(self, version):
    '''Returns a list of books for a given version'''
    return Verse.objects.filter(version__iexact=version)
  
  def get_book_names(self, verses):
    '''Returns a list of unique book names'''
    books = []
    for verse in verses:
      book = verse.book
      if book not in books:
        books.append(book)
    return books

  def get_chapters(self, version, book):
    '''Returns a list of verses for a given version and book'''
    #TODO: I'd like to find a way to do a distinct here, rather than afterward...
    #I'd also like to NOT have to break up my model to do so
    return Verse.objects.filter(version__iexact=version, book__iexact=book)

  def get_chapter_numbers(self, verses):
    '''Returns a list of unique chapter numbers'''
    chapters = []
    for verse in verses:
      chapter = verse.chapter
      if chapter not in chapters:
        chapters.append(chapter)
    return chapters
  
  def get_verses(self, version, book, chapter):
    '''Returns a list of verses for a given version, book, and chapter'''
    return Verse.objects.filter(version__iexact=version, book__iexact=book, chapter__iexact=chapter)

  def get_verse(self, version, book, chapter, verse):
    '''Returns an exact verse'''
    return Verse.objects.filter(version__iexact=version, book__iexact=book, chapter__iexact=chapter, verse__iexact=verse)

  def get_verses_range(self, version, book, chapter, verse, verse2):
    '''Returns a list of verses in a given range'''
    return Verse.objects.filter(version__iexact=version, book__iexact=book, chapter__iexact=chapter, verse__in=range(int(verse),int(verse2)+1))
  
  def get_verses_or_404(self, version, book, chapter, verse, verse2):
    '''Returns a list of verses or Raises Http404'''
    if verse is None:
      verses = Verse().get_verses(version, book, chapter)
    elif verse2 is None:
      verses = Verse().get_verse(version, book, chapter, verse)
    else:
      if verse2 < verse:
        raise Http404
      verses = Verse().get_verses_range(version, book, chapter, verse, verse2)

    if verses.count() == 0:
      raise Http404

    return verses
