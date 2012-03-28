#!/usr/bin/python
import site
from settings import *
site.addsitedir(os.path.join(ROOT_DIR, 'thirdparty'))

from flask import Flask, request, session, redirect, render_template, Response
from flask.helpers import make_response
import pcutils
from werkzeug.routing import BaseConverter


app = Flask(__name__)
app.config.from_object(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter
#@app.route('/<regex("[abcABC0-9]{4,6}"):uid>-<slug>/')


#@app.route('/', defaults=dict(path_info=''))
#@app.route('/<path:path_info>')
@app.route('/')
def index():
    response = make_response(
        render_template("index.html")
    )
    return response

@app.route('/<int:width>')
@app.route('/<int:width>x')
@app.route('/x<int:height>')
def img(width=0, height=0):
    try:
        im = pcutils.simple_resize(width, height, ROOT_DIR + '/static/' + DEFAULT_GALLERY + '/default.jpg')
        response = pcutils.get_jpeg_response(im)
        return response
    except IOError, ioe:
        return make_response('An error occurred.  Sorry.')

@app.route('/<int:width>x<int:height>')
def imgar(width, height):
    """ Find the most appropriate aspect ratio corgi, fit it to the new size, and then crop nicely. """
    im = pcutils.super_fit(width, height, ROOT_DIR + '/static/corgi/*')
    response = pcutils.get_jpeg_response(im)
    return response

@app.route('/<gallery>/<int:width>x<int:height>')
def imgar_gallery(gallery, width, height):
    """ Find the most appropriate aspect ratio corgi, fit it to the new size, and then crop nicely. """
    im = pcutils.super_fit(width, height, ROOT_DIR + '/static/' + gallery + '/*')
    if im is None:
        return make_response('An error occurred.  You probably specified an invalid gallery.')
    response = pcutils.get_jpeg_response(im)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
