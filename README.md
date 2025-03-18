# Fuzzy Matching

## Goal

This package allows you to use fuzzy matching on multiple attributes. Each attribute can
define its own matching algoritm. Attribute similarity scores are combined into a final
score using configurable weights. Results are ranked using this final similarity score.

Available matching algoritms:

- Edit distance: Levenshtein, Damerau-Levenshtein, Optimal String Alignment.
- Cosine similarity between subword vectors.
- Datetime deltas.

## Installation

### For regular users

You can install this package using pip:

```shell
python -m pip install git+https://github.com/LFKoning/fuzzy-matching
```

This will install the package and all of its dependencies into your current Python
environment.

### For developers

If you want to help develop this project, please follow these steps.
First, clone the project to your machine:

```shell
git clone https://github.com/LFKoning/fuzzy-matching
```

Then install the package and its development dependencies using pip:

```shell
python -m pip install -e .[dev]
```

Finally, if you want to read the HTML documentation generated by `mkdocs` use:

```shell
python -m pip install -e .[dev,docs]
```

## Usage

To use this package, first generate an encryption key like so:

```python
from fuzzy_matching.encryption import AESGCM4Encryptor

encryption_key = AESGCM4Encryptor.generate_key()
```

Next configure the attributes you want to match on:

```python
config = {
    "name": {
        "algoritm": "vector",
        "weight": 0.6,
    },
    "birthdate": {
        "algoritm": "timedelta",
        "format": "%d-%m-%Y",
        "weight": 0.2,
    },
    "address": {
        "algoritm": "levenshtein",
        "weight": 0.2,
    },
}
```

Then create a `MultiMatcher` object to perform the matching:

```python
from fuzzy_matching.match_multi import MultiMatcher


matcher = MultiMatcher(
    top_n=10,                           # Number of results to return.
    config=config,                      # Field configuration.
    encryption_key=encryption_key,      # Generated encryption key.
    storage_path="storage"              # Folder to store the data in.
)
```

Now you are ready to add some data:

```python
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2],
    "name": ["John Doe", "Jane Doe"],
    "birthdate": ["1-1-1999", "2-2-1999"],
    "address": ["Johnstreet 1", "Janestreet 2"],
})

matcher.create(df, id_column="id")
```

And finally, you can match against a target:

```python
matcher.get({
    "name": "Johny Doe",
    "birthdate": "10-10-1999",
    "address": "Somestreet 1",
})
```

## Documentation

Documentation for this project can be generated using `mkdocs`. To build and view the
HTML documentation, go to the root folder and type:

```shell
mkdocs serve
```

Open a webbrowser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to browse
the documentation.

The documentation for the code is automatically extracted from (numpy) docstrings. Other
pages can be found and edited in the `docs` folder.

## Contributing

If you want to contribute to this project, feel free to clone the code, make
improvements and open a pull request!

If you have suggestions or remarks not directly related to the project's code or
documentation, feel free to e-mail the authors.

## Maintainers

This project is maintained by:

1. Lukas Koning (lfkoning@gmail.com)
