import datetime
import math
import random
import re
import tempfile
import titlecase
import twitter
import yaml

from image_generation import create_image, crop_image
from stuff import titles, tasks, things, datas, adjectives, data_qualifiers, task_qualifiers


def choose(lst):
    n = len(lst)
    i = random.randint(0, n - 1)
    return lst[i]


def maybe(p=0.5):
    return lambda _: random.random() < p


def simplify(string):
    string = re.sub(" +", " ", string).strip()  # Remove multiple spaces
    string = titlecase.titlecase(string)
    return string


title = choose(titles)
net_qualifiers = " ".join(filter(maybe(0.20), adjectives))
task = choose(tasks)
task_qualifier = choose(task_qualifiers)
thing = choose(things)
data = choose(datas)
data_qualifier = choose(data_qualifiers)

kwargs = {
    "title": title,
    "net_qualifiers": net_qualifiers,
    "task_qualifier": task_qualifier,
    "data_qualifier": data_qualifier,
    "task": task,
    "thing": thing,
    "data": data,
}

templates = [
    f"{title}Net: a {net_qualifiers} neural network for {task} of {thing} in {data_qualifier} {data}",
    f"Deep{title}: {task_qualifier} {net_qualifiers} networks for {thing} {task} using {data_qualifier} {data}",
    f"{task_qualifier} {thing} {task} using the {net_qualifiers} {title.upper()} model on {data_qualifier} {data}",
]


if __name__ == "__main__":
    template = choose(templates)
    title = simplify(template)
    n_authors = math.ceil(2 * random.lognormvariate(0, 0.5))
    n_institutions = math.ceil(2 * random.lognormvariate(0, 0.5))
    with open("authors.txt") as fp:
        authors = list(map(str.strip, fp.readlines()))
    authors = random.sample(authors, n_authors)
    with open("institutions.txt") as fp:
        institutions = list(map(str.strip, fp.readlines()))
    institutions = random.sample(institutions, n_institutions)
    if n_authors <= 3:
        author_list = ", ".join(authors)
    else:
        author_list = authors[0] + " et al."

    date = datetime.datetime.now().strftime("%y%m.%d%H%M")
    text = f'"{title}" from {author_list}, SnarXiv id: {date}'
    print(text)

    image = create_image(title, authors, institutions)
    image = crop_image(image)
    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
        image.save(tmp.name)

    with open("api_keys.yaml", "r") as fp:
        api_config = yaml.load(fp)
    api = twitter.Api(**api_config)
    statuts = api.PostUpdate(text, media="test.png")
