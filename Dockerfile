FROM public.ecr.aws/docker/library/python:3.12.8

LABEL maintainer="tortxof@gmail.com"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --frozen

CMD ["uv", "run", "gunicorn", "rc_club_members.wsgi"]
