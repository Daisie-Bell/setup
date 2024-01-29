# How to start using Svaeva SDK

## install poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

## Start Environment FIle

```bash
poetry init
```

## Start or enveronment

```bash
poetry shell
```

## Installation

```bash
poetry add https://github.com/Daisie-Bell/svaeva-sdk.git
```

### What to do next

Start using the SDK [Link to the documentation](https://github.com/Daisie-Bell/svaeva-sdk#client-api)

```python
from svaeva import Svaeva

svaeva = Svaeva()
```

### Add a platform in to your Svaeva account

```python
svaeva.database.platform.telegram = ["username"]
```
You can also add a custom platform to your account more information [here](https://github.com/Daisie-Bell/svaeva-sdk#platform)

[Link to local example](add_platform.py)
