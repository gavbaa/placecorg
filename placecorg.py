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
@app.route('/<int:width>.<ext>')
@app.route('/<int:width>x.<ext>')
@app.route('/x<int:height>.<ext>')
def img(width=0, height=0, ext=''):
    try:
        im = pcutils.simple_resize(width, height, ROOT_DIR + '/static/' + DEFAULT_GALLERY + '/default.jpg')
        response = pcutils.get_extension_response(im, ext)
        return response
    except IOError, ioe:
        return make_response('An error occurred.  Sorry.')

@app.route('/<int:width>x<int:height>')
@app.route('/<int:width>x<int:height>.<ext>')
def imgar(width, height, ext=''):
    return imgar_gallery(DEFAULT_GALLERY, width, height, ext)

@app.route('/<gallery>/<int:width>x<int:height>')
@app.route('/<gallery>/<int:width>x<int:height>.<ext>')
def imgar_gallery(gallery, width, height, ext=''):
    """ Find the most appropriate aspect ratio corgi, fit it to the new size, and then crop nicely. """
    im = pcutils.super_fit(width, height, ROOT_DIR + '/static/' + gallery + '/*')
    if im is None:
        return make_response('An error occurred.  You probably specified an invalid gallery.')
    im = pcutils.additional_image_mangling(im, request.args)
    response = pcutils.get_extension_response(im, ext)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
