import fitz
import itertools
import math
import numpy as np
import tempfile
import random
import os

from PIL import Image, ImageOps
from pylatex import Document, Command
from pylatex.utils import NoEscape


def pdf_to_png(pdf_file, resolution=200, n_pages=None, alpha=True):
    """ Converts a PDF file into a list of PNG images.

    Arguments:
        pdf_file {str} -- path to a PDF file

    Keyword Arguments:
        resolution {int} -- resolution in DPI for rasterization (default: {150})
        n_pages {int} -- maximum number of pages to get, if None keep going until no page is left.
                        (default: {None})
        alpha {bool} -- True to keep the alpha channel when converting to PNG, False to drop it.
                        Some PDF files have a transparent background which makes the text illegible
                        in PNG format. (default: {True})

    Yields:
        generator of Pillow images (one per page)
    """
    zoom = resolution / 96.0
    pdf = fitz.Document(pdf_file)
    for page in itertools.islice(pdf, n_pages):
        pix = page.getPixmap(matrix=fitz.Matrix(zoom, zoom), alpha=alpha)
        yield Image.frombuffer("RGB", [pix.width, pix.height], pix.samples, "raw", "RGB", 0, 1)


def create_image(title, authors, institutions):
    n_institutions = len(institutions)
    doc = Document()
    doc.preamble.append(Command("usepackage", "authblk"))
    doc.preamble.append(Command("title", title))
    for author in authors:  # List the authors
        idx = random.sample(
            range(1, n_institutions + 1),
            min(n_institutions, math.ceil(1 * random.lognormvariate(0, 0.5))),
        )
        doc.preamble.append(Command("author", NoEscape(author), options=sorted(idx)))
    for idx, institution in enumerate(institutions):  # List the affiliations
        doc.preamble.append(Command("affil", NoEscape(institution), options=[idx + 1]))
    doc.preamble.append(Command("date", NoEscape(r"\today")))  # Use today's date
    doc.append(NoEscape(r"\maketitle"))  # Generate the title
    doc.append(Command("thispagestyle", "empty"))  # Do not show the page number
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as temp:
        temp_filename, _ = os.path.splitext(temp.name)
        doc.generate_pdf(temp_filename, clean_tex=True)
        image = list(pdf_to_png(temp.name, n_pages=1, alpha=False, resolution=300))[0]
    return image


def crop_image(image):
    # Convert to numpy array for easier manipulation
    im = np.asarray(image)
    mask = ~im
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    cropped = im[rmin:rmax, cmin:cmax]
    image = Image.fromarray(cropped.astype("uint8"), "RGB")
    return ImageOps.expand(image, 20, fill="white")
