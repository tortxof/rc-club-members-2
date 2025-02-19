FROM public.ecr.aws/docker/library/python:3.12.8

LABEL maintainer="tortxof@gmail.com"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --frozen

RUN uv run ./manage.py collectstatic

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8000", "rc_club_members.wsgi"]
