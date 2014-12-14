import sys
import os

from datetime import date, datetime
from flask import Flask, render_template, redirect, abort
from flask_flatpages import FlatPages
from flaskext.markdown import Markdown
from flask.ext.assets import Environment as AssetManager
from flask_frozen import Freezer


# configuration
REPO_NAME = "gleeguesite"
REPO = ""    # default REPO is '', while serving or building the '/' + REPO_NAME is assigned to it
APP_DIR = os.path.dirname(os.path.abspath(__file__))

#def parent_dir(path):
#    '''Return the parent of a directory.'''
#    return os.path.abspath(os.path.join(path, os.pardir))

PROJECT_ROOT = APP_DIR
# In order to deploy to Github pages, you must build the static files to
# the project root
FREEZER_DESTINATION = PROJECT_ROOT
# Since this is a repo page (not a Github user page),
# we need to set the BASE_URL to the correct url as per GH Pages' standards
FREEZER_BASE_URL = "http://localhost/{0}".format(REPO_NAME)
FREEZER_REMOVE_EXTRA_FILES = False  # IMPORTANT: If this is True, all app files
                                    # will be deleted when you run the freezer

DEBUG = True
TESTING = True
ASSETS_DEBUG = DEBUG
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
#FLATPAGES_ROOT = 'pages'
FLATPAGES_ROOT = os.path.join(APP_DIR, 'pages')
#FREEZER_RELATIVE_URLS = True
# App configuration
SECTION_MAX_LINKS = 12

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)
markdown_manager = Markdown(app, extensions=['fenced_code'], output_format='html5',)
asset_manager = AssetManager(app)

###############################################################################
# Model helpers

def get_pages(pages, offset=None, limit=None, section=None, year=None):
    """ Retrieves pages matching passec criterias.
    """
    articles = list(pages)
    # assign section value if none was provided in the metas
    for article in articles:
        if not article.meta.get('section'):
            article.meta['section'] = article.path.split('/')[0]
    # filter unpublished article
    if not app.debug:
        articles = [p for p in articles if p.meta.get('published') is True]
    # filter section
    if section:
        articles = [p for p in articles if p.meta.get('section') == section]
    # filter year
    if year:
        articles = [p for p in articles if p.meta.get('date').year == year]
    # sort by date
    articles = sorted(articles, reverse=True, key=lambda p: p.meta.get('date',
        date.today()))
    # assign prev/next page in serie
    for i, article in enumerate(articles):
        if i != 0:
            if section and articles[i - 1].meta.get('section') == section:
                article.prev = articles[i - 1]
        if i != len(articles) - 1:
            if section and articles[i + 1].meta.get('section') == section:
                article.next = articles[i + 1]
    # offset and limit
    if offset and limit:
        return articles[offset:limit]
    elif limit:
        return articles[:limit]
    elif offset:
        return articles[offset:]
    else:
        return articles

def get_years(pages):
    years = list(set([page.meta.get('date').year for page in pages]))
    years.reverse()
    return years

def section_exists(section):
    return not len(get_pages(pages, section=section)) == 0

###############################################################################
# Routes

@app.route('/')
def index():
    return render_template('index.html', pages=pages, repo=REPO)

@app.route('/<path:path>/')
def page(path):
    # compute current "section" from path
    section = path.split('/')[0]
    #print section
    page = pages.get_or_404(path)
    #print page
    #print "page: ", page
    # ensure an accurate "section" meta is available
    page.meta['section'] = page.meta.get('section', section)
    # allow preview of unpublished stuff in DEBUG mode
    if not app.debug and not page.meta.get('published', False):
        abort(404)
    template = page.meta.get('template', '%s/page.html' % section)
    return render_template(template, page=page, section=section)


@app.route('/<string:section>/')
def section(section):
    #print "section: ", section
    if not section_exists(section):
        print "I am here"
        abort(404)
    template = '%s/index.html' % section
    #print template
    articles = get_pages(pages, limit=SECTION_MAX_LINKS, section=section)
    #print "art:", articles
    years = get_years(get_pages(pages, section=section))
    return render_template(template, pages=articles, years=years, repo=REPO)

#@app.route('/sublocator/')
#def sublocator():
#    return redirect("https://docs.google.com/spreadsheets/d/1-TsLhg2NbzardgX6KckQM_p5O5VMesYYabcnwR09fZ0", code=302)

"""
@app.route('/photos/')
def photos():
    return render_template("photos/photos.html")

#@app.route('/wiki/')
#def wiki():
#    return redirect("http://gleegue.wikidot.com/", code=302)

@app.route('/blog/')
def blog():
    return render_template("blog/blogs.html")

@app.route('/track/')
def track():
    return render_template("track/tracking-sheets.html")

@app.route('/<path:path>/')
def page(path):
    return pages.get_or_404(path).html
"""

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        app.debug = False
        REPO = '/'+REPO_NAME
        asset_manager.config['ASSETS_DEBUG'] = False
        freezer.freeze()
    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        freezer.serve(port=4000)
    else:
        app.run(port=8000)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            