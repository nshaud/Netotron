import datetime
import logging
import math
import random
import re
import sys
import tempfile
import titlecase
import twitter
import warnings
import yaml

from image_generation import create_image, crop_image
from stuff import adjectives, data_qualifiers, datas, task_qualifiers, tasks, things, titles

# Ignore ResourceWarning due to unclosed SSLSocket by the Twitter http request
warnings.simplefilter("ignore", ResourceWarning)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(stream=sys.stdout)
hdlr.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
logger.addHandler(hdlr)


def choose(lst):
    n = len(lst)
    i = random.randint(0, n - 1)
    return lst[i]


def maybe(p=0.5):
    return lambda _: random.random() < p


def format_title(string: str) -> str:
    string = re.sub(" +", " ", string).strip()  # Remove multiple spaces
    string = titlecase.titlecase(string)
    return string


def generate_title() -> str:
    title = choose(titles)
    net_qualifiers = " ".join(filter(maybe(0.20), adjectives))
    task = choose(tasks)
    task_qualifier = choose(task_qualifiers)
    thing = choose(things)
    data = choose(datas)
    data_qualifier = choose(data_qualifiers)
    templates = [
        f"{title}Net: a {net_qualifiers} neural network for {task} of {thing} in {data_qualifier} {data}",
        f"Deep{title}: {task_qualifier} {net_qualifiers} networks for {thing} {task} using {data_qualifier} {data}",
        f"{task_qualifier} {thing} {task} using the {net_qualifiers} {title.upper()} model on {data_qualifier} {data}",
    ]
    return format_title(choose(templates))


if __name__ == "__main__":
    try:
        # Generate a random article title
        title = generate_title()
        # How many authors?
        n_authors = math.ceil(2 * random.lognormvariate(0, 0.5))
        # How many institutions?
        n_institutions = math.ceil(2 * random.lognormvariate(0, 0.5))
        # Sample authors
        with open("authors.txt") as fp:
            authors = list(map(str.strip, fp.readlines()))
        authors = random.sample(authors, n_authors)
        # Sample institutions
        with open("institutions.txt") as fp:
            institutions = list(map(str.strip, fp.readlines()))
        institutions = random.sample(institutions, n_institutions)

        # Format author list
        if n_authors <= 3:  # List all authors if less than 3
            author_list = ", ".join(authors)
        else:  # Else use "First Author et al."
            author_list = authors[0] + " et al."

        # Generate fake arXiv identifier
        identifier = datetime.datetime.now().strftime("%y%m.%d%H%M")
        text = f'[Parody] New paper:"{title}" from {author_list}, SnarXiv id: {identifier}'
        logger.debug(f"Tweet generated: {text}")

        # Generate fake PDF screenshot
        image = create_image(title, authors, institutions)
        image = crop_image(image)
        logger.debug("LaTeX -> PDF -> image generation done")

        # Publish to Twitter
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            image.save(tmp.name)  # Save image in temporary file
            logger.debug(f"Writing image at {tmp.name}")

            with open("api_keys.yaml", "r") as fp:  # Load API keys
                api_config = yaml.load(fp, Loader=yaml.BaseLoader)
            api = twitter.Api(**api_config)
            # Post status to Twitter
            status = api.PostUpdate(text, media=tmp.name)
            logger.info(f"Sent update to Twitter")
    except Exception as e:
        logger.exception(f"Error during tweet generation: {e}")
