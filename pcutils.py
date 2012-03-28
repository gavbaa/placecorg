from flask.helpers import make_response
import glob
from PIL import Image, ImageDraw, ImageFont, ImageOps
import StringIO

def additional_image_mangling(im, get):
    if get.get('g', False):
        im = ImageOps.grayscale(im)
    if get.get('d', False):
        # Stamp the image dimensions on
        f = ImageFont.load_default()
        d = ImageDraw.Draw(im)
        im_dims = '(%s,%s)' % (im.size[0], im.size[1])
        text_size = d.textsize(im_dims)
        d.rectangle((im.size[0] - text_size[0], im.size[1] - text_size[1], im.size[0], im.size[1]), fill=0xffffff)
        d.text((im.size[0] - text_size[0], im.size[1] - text_size[1]), im_dims,  font=f, fill=0x000000)
    return im

def simple_resize(width, height, path):
    im = Image.open(path)
    ar = float(im.size[0]) / im.size[1]
    #print 'ar', ar

    if not height:
        height = int(width / ar)
    if not width:
        width = int(height * ar)

    #im.thumbnail((width, width), Image.ANTIALIAS)
    im = im.resize((width, height), Image.ANTIALIAS)
    return im

def super_fit(width, height, dir):
    """
    Given a width, height and directory of images, find the most appropriate image in the directory that fits
    those dimensions, and resize/crop appropriately.  Return the cropped raw image object.
    """
    img_paths = glob.glob(dir)
    if len(img_paths) == 0:
        return None

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
    #print img_ars
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
    return im

def get_extension_response(im, ext=''):
    if ext == 'png':
        return get_png_response(im)
    elif ext == 'jpg' or ext == 'jpeg' or ext == '':
        return get_jpeg_response(im)
    raise Exception('Unrecognized extension given: ' + ext)


def get_jpeg_response(im):
    """ Given an image object, create a Flask response with the appropriate headers. """
    # Spit it out.
    buf = StringIO.StringIO()
    im.save(buf, format= 'JPEG')
    jpeg = buf.getvalue()
    buf.close()
    response = make_response(jpeg)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

def get_png_response(im):
    """ Given an image object, create a Flask response with the appropriate headers. """
    # Spit it out.
    buf = StringIO.StringIO()
    im.save(buf, format= 'PNG')
    jpeg = buf.getvalue()
    buf.close()
    response = make_response(jpeg)
    response.headers['Content-Type'] = 'image/png'
    return response
