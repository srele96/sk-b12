# sk-b12

Send a CV via pipeline.

## Test server

Use the echo server for testing purposes:

```
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
GITHUB_RUN_ID=
DATA_SHA_HMAC_SECRET=
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
