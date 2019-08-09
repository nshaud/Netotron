FROM python:3.7.4-slim-buster

RUN apt update && apt install -y mupdf latexmk texlive-latex-extra
COPY . /work/
WORKDIR /work/
RUN pip install poetry && poetry config settings.virtualenvs.create false
RUN poetry install
CMD ["python", "netotron.py"]