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
from typing import List


def pdf_to_png(file: str, resolution: int = 200, n_pages: int = None, alpha: bool = True) -> Image:
    """ Converts a PDF file into a list of PNG images.

    Arguments:
    file {str} -- path to a PDF file

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
    pdf = fitz.Document(file)
    for page in itertools.islice(pdf, n_pages):
        pix = page.getPixmap(matrix=fitz.Matrix(zoom, zoom), alpha=alpha)
        yield Image.frombuffer("RGB", [pix.width, pix.height], pix.samples, "raw", "RGB", 0, 1)


def create_image(title: str, authors: List[str], institutions: List[str]) -> Image:
    """ Generates an image of a fake article header using the title, author and institution lists.

    Arguments:
        title {str} -- name of the article
        authors {str list} -- list of author names
        institutions {str list} -- list of author affiliations

    Returns:
        PIL.Image -- a snapshot of the PDF file
    """
    n_institutions = len(institutions)
    # Generate the LaTeX documenet
    doc = Document()
    doc.preamble.append(Command("usepackage", "authblk"))  # Used for author affiliations
    doc.preamble.append(Command("title", title))  # Set the title
    for author in authors:  # List the authors
        # Add a random institution to the author
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
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp:
        # Compile the LaTeX document in a temporary file
        temp_filename, _ = os.path.splitext(temp.name)
        doc.generate_pdf(temp_filename, clean_tex=True)
        # Use PyMuPDF to convert the PDF into a PNG
        image = list(pdf_to_png(temp.name, n_pages=1, alpha=False, resolution=300))[0]
    return image


def crop_image(image):
    """ Crops an image by removing all extra white space around the content (i.e. zoom on the actual
        content bounding rectangle).

    Arguments:
        image {PIL.Image} -- the input image

    Returns:
        PIL.Image -- the cropped result
    """
    # Convert to numpy array for easier manipulation
    im = np.asarray(image)
    # Crop the image by removing all extra white space
    mask = ~im
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    cropped = im[rmin:rmax, cmin:cmax]
    # Convert back to PIL Image
    image = Image.fromarray(cropped.astype("uint8"), "RGB")
    # Add 20px white padding
    image = ImageOps.expand(image, 20, fill="white")
    return image
