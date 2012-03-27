#!/usr/bin/python
import json
from PIL import Image
import urllib2
from urllib import urlencode
from werkzeug.routing import BaseConverter

import StringIO
import site, os
import settings

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.join(ROOT_DIR, 'thirdparty'))

DEBUG = True
SECRET_KEY = 'LatitnoywenfevyethCasacbaroncab3' # flask secret key

from flask import Flask, request, session, redirect, render_template, Response
from flask.helpers import make_response
from functools import wraps
import requests

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
    print width, height
    try:
        im = Image.open(ROOT_DIR + '/static/ph/220x220.jpg')
        ar = float(im.size[0]) / im.size[1]
        #print 'ar', ar

        if not height:
            height = int(width / ar)
        if not width:
            width = int(height * ar)

        #im.thumbnail((width, width), Image.ANTIALIAS)
        im = im.resize((width, height), Image.ANTIALIAS)
        buf = StringIO.StringIO()
        im.save(buf, format= 'JPEG')
        jpeg = buf.getvalue()
        buf.close()
        response = make_response(jpeg)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    except IOError, ioe:
        return make_response('')

def available_images():
    import glob
    g = glob.glob(ROOT_DIR + '/static/ph/*')
    return g

@app.route('/<int:width>x<int:height>')
def imgar(width, height):
    """ Find the most appropriate aspect ratio corgi, fit it to the new size, and then crop nicely. """
    img_paths = available_images()
    imgs = {}
    img_by_ars = {}
    img_ars = []
    for i in img_paths:
        try:
            im = Image.open(i)
            imgs[i] = im
            ar = float(im.size[0]) / im.size[1]
            img_ars.append(ar)
            img_by_ars[ar] = im
        except IOError, ioe:
            pass

    img_ars.sort()
    print img_ars
    ar = float(width) / height

    # Find the nearest aspect ratio.
    ix = 0
    while ix < len(img_ars) - 1:
        if ar - img_ars[ix] <= 0.01:
            break
        ix += 1

    #print ar, ix

    if ix == 0:
        pass
    else:
        ar_center = img_ars[ix] - (img_ars[ix] - img_ars[ix - 1]) / 2
        #print ar_center
        if ar < ar_center:
            ix -= 1

    im = img_by_ars[img_ars[ix]]

    # Resize to a size that fits both dimensions, then crop.
    resize_factor = max(float(width) / im.size[0], float(height) / im.size[1])
    resizers = (int(im.size[0] * resize_factor), int(im.size[1] * resize_factor))
    im = im.resize(resizers, Image.ANTIALIAS)

    top = 0
    left = 0
    if resizers[0] > width:
        left = -int((width - resizers[0]) / 2)
    if resizers[1] > height:
        top = -int((height - resizers[1]) / 2)

    # PIL docs: The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    im = im.crop((left, top, left + width, top + height))

    # Spit it out.
    buf = StringIO.StringIO()
    im.save(buf, format= 'JPEG')
    jpeg = buf.getvalue()
    buf.close()
    response = make_response(jpeg)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

