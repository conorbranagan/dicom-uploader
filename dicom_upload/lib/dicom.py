""" Dicom helper functions.

    PIL functions taken from:
        https://github.com/darcymason/pydicom/blob/master/pydicom/contrib/pydicom_PIL.py
"""
# stdlib
from datetime import datetime

# 3p
import PIL.Image
import numpy as np


def get_LUT_value(data, window, level):
    """ Apply the RGB Look-Up Table for the given data and window/level value.
    """
    f = lambda data: ((data - (level - 0.5)) / (window - 1) + 0.5) * (255 - 0)
    return np.piecewise(data, [
        data <= (level - 0.5 - (window - 1) / 2),
        data > (level - 0.5 + (window - 1) / 2)
    ], [0, 255, f])


def pil_from_dataset(ds):
    """ Convert a Dicom dataset to a PIL image. """
    if 'PixelData' not in ds:
        raise TypeError("DICOM dataset is missing pixel data.")

    # Can only apply LUT if these values exist.
    if 'WindowWidth' not in ds or 'WindowCenter' not in ds:
        bits = ds.BitsAllocated
        samples = ds.SamplesPerPixel
        if bits == 8 and samples == 1:
            mode = "L"
        elif bits == 8 and samples == 3:
            mode = "RGB"
        elif bits == 16:
            mode = "I;16"
        else:
            raise TypeError("Don't know PIL mode for %d BitsAllocated and %d "
                            "SamplesPerPixel" % (bits, samples))

        # PIL size = (width, height)
        size = (ds.Columns, ds.Rows)
        im = PIL.Image.frombuffer(mode, size, ds.PixelData, "raw", mode, 0, 1)
    else:
        image = get_LUT_value(ds.pixel_array, ds.WindowWidth, ds.WindowCenter)
        im = PIL.Image.fromarray(image).convert('L')

    # Return as RGB so we can save it as a common image format.
    return im.convert('RGB')


def parse_date(raw_date):
    """ Example expected format: 20050101 """
    date_format = '%Y%m%d'
    return datetime.strptime(raw_date, date_format)


def parse_age(raw_age):
    """ Example expected format: 027Y """
    return int(raw_age[1:-1])
