import datetime
import math
import random
import re
import twitter
import yaml

from image_generation import create_image, crop_image


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


titles = [
    "Cheese",
    "Church",
    "Toulouse",
    "Paris",
    "Plane",
    "SEX",
    "Pirate",
    "Ninja",
    "Fishnet",
    "Gladiator",
    "CVPR",
    "Auto",
    "HyperDeep",
    "AUTHOR",
    "NONAME",
    "[ReplaceBeforeSubmission]",
    "Brain",
    "Universal",
    "Killer",
]
tasks = [
    "classification",
    "detection",
    "segmentation",
    "instance segmentation",
    "removal",
    "inpainting",
    "topic modeling",
    "style transfer",
    "super-resolution",
    "denoising",
    "zero-shot learning",
]
things = [
    "rabbits",
    "cats",
    "microwaves",
    "alien signals",
    "racism",
    "bats",
    "super-heroes",
    "mac&cheese",
    "glasses",
    "beer foam",
    "outliers",
    "nanorobots",
    "lost treasures",
    "chickens",
    "dogs",
    "raccoons",
    "thiefs",
    "hair",
    "majijuana",
    "vehicles",
    "Boeing 737-MAX",
    "fake money",
    "giftable Eiffel Tower miniatures",
]
datas = [
    "RGB images",
    "brain-electro-activities",
    "children books",
    "fisheye videos",
    "Dailymotion comments",
    "Reddit usernames",
    "open source code",
    "satellite images",
    "3D point clouds",
    "missing data",
    "StreetView panoramas",
    "Tinder profile pictures",
    "vacation pictures",
    "autonomous vehicles sensors",
    "PET scans",
    "3D models",
    "stereo imaging",
    "RGB-D data",
    "raw Apache logs",
    "disassembled Java",
    "ATM receipts",
    "traffic cameras",
    "user webcams",
    "HDR pictures",
    "3D movies",
    "radar, sonar and that last one that uses light",
]

data_qualifiers = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "noisy labeled",
    "industrial",
    "expensive",
    "unlabeled",
]
task_qualifiers = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "improving",
    "pushing further",
    "better",
    "SOTA",
    "weakly-supervised",
    "semi-supervised",
]

title = choose(titles)
net_qualifiers = " ".join(
    filter(
        maybe(0.20),
        [
            "new",
            "reinforcement learning of",
            "lightweight",
            "scalable",
            "embedded",
            "deep",
            "adversarial",
            "residual",
            "convolutional",
            "recurrent",
        ],
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
