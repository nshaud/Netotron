import datetime
import math
import random
import re
import twitter
import yaml

from image_generation import create_image, crop_image
from stuff import titles, things, datas, adjectives, data_qualifiers, task_qualifiers

def choose(lst):
    n = len(lst)
    i = random.randint(0, n - 1)
    return lst[i]


def maybe(p=0.5):
    return lambda _: random.random() < p


def simplify(string):
    string = re.sub(" +", " ", string)  # Remove multiple spaces
    string = " ".join(w[:1].upper() + w[1:] for w in string.split(" "))  # Capitalize first words
    return string



title = choose(titles)
net_qualifiers = " ".join(
    filter(
        maybe(0.20),
        adjectives
    )
)
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
    "{title}Net: a {net_qualifiers} neural network for {task} of {thing} in {data_qualifier} {data}",
    "Deep{title}: {task_qualifier} {net_qualifiers} networks for {thing} {task} from {data_qualifier} {data}",
    "{task_qualifier} {thing} {task} using the {net_qualifiers} {title} model on {data_qualifier} {data}",
]


if __name__ == "__main__":
    template = choose(templates)
    title = simplify(template.format(**kwargs))
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

    date = datetime.datetime.now().strftime("%Y%m%d%H%M")
    text = f'"{title}" from {author_list}, SnarXiv id: {date}'
    print(text)

    #image = create_image(title, authors, institutions)
    #image = crop_image(image)
    #image.save("test.png")

    with open("api_keys.yaml", "r") as fp:
        api_config = yaml.load(fp)
    api = twitter.Api(**api_config)
    statuts = api.PostUpdate(text, media="test.png")
