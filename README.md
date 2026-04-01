# sk-b12

Send a CV via pipeline.

## Thank you

This project was cool, i loved it! This was one of the most interesting applications i have sent. Actually, this was probably the most interesting application i had to send. Imagine writing code to actually submit a cv. Haven't seen this one in other job postings so far. Props to the people responsible for the idea. Hope you have a good time finding the right candidate.

## High level explanation

- The script sends an application
- The workflow uses custom image to clone the repo and run the script. The workflow variables encapsulate secrets and inject them into the ENVIRONMENT.
- The custom image acts as an empty shell with prepared tools required to build the project
- The automated script to build and publish a docker image to github
- The workflow to build and publish custom docker image
- The workflow to submit an application

_Note: Here i did a similar thing a while ago <https://github.com/srele96/sk-experiments/tree/develop/docker/experiments/play_with_docker>._

## Test server

Use the echo server for testing purposes:

```env
https://echo.free.beeceptor.com
```

## Create env file

```env
DATA_URL=
DATA_NAME=
DATA_EMAIL=
DATA_RESUME_LINK=
DATA_REPOSITORY_LINK=
DATA_ACTION_RUN_LINK=
DATA_SHA_HMAC_SECRET=
SUBMIT_APPLICATION=
DEBUG=
```

## Documentation

Install [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file) package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you don't have virutal environment, run:

```bash
uv venv
```

Or run to create virtual environment and install dependencies:

```bash
uv sync
```

Open venv in current shell:

```
source env/bin/activate
```

Add a new dependency (for example, flask):

```bash
uv add flask
```

And, run the script:

```bash
python main.py
```
