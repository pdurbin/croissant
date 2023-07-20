"""Migrates Croissant configs.

Migration from an older or non canonical Croissant format to a canonical and possibly
newer Croissant format.
"""

import json
import importlib

from absl import app
from absl import flags
from etils import epath
from ml_croissant._src.core.json_ld import expand_json_ld, compact_json_ld


_PREVIOUS_MIGRATIONS_FOLDER = "previous"

flags.DEFINE_string(
    "migration",
    None,
    "The name of the Python file with the migration.",
)

FLAGS = flags.FLAGS


def get_migration_fn(migration: str | None):
    """Retrieves the `up` migration function from the migration file if it exists."""
    if migration is None:

        def identity_function(x):
            return x

        return identity_function
    try:
        mod = importlib.import_module(f"{_PREVIOUS_MIGRATIONS_FOLDER}.{migration}")
    except ImportError as e:
        raise ValueError(
            "Did you create a file in named"
            f" {_PREVIOUS_MIGRATIONS_FOLDER}/{migration}.py?"
        ) from e
    try:
        return getattr(mod, "up")
    except AttributeError as e:
        raise ValueError(
            f"Does the file {_PREVIOUS_MIGRATIONS_FOLDER}/{migration}.py declare a `up`"
            " function?"
        ) from e


def main(argv):
    """Main function launched for the migration."""
    del argv
    # Datasets in croissant/datasets
    datasets = [path for path in epath.Path("../../datasets").glob("*/*.json")]
    # Datasets in croissant/python/ml_croissant/_src/tests
    datasets += [
        path for path in epath.Path("ml_croissant/_src/tests/graphs").glob("*.json")
    ]
    for dataset in datasets:
        print(f"Converting {dataset}...")
        with dataset.open("r") as f:
            json_ld = json.load(f)
            up = get_migration_fn(FLAGS.migration)
            json_ld = up(json_ld)
            json_ld = compact_json_ld(expand_json_ld(json_ld))
        with dataset.open("w") as f:
            # Special cases for test datasets without @context
            if dataset.name == "recordset_missing_context_for_datatype.json":
                del json_ld["@context"]["dataType"]
            if dataset.name == "mlfield_missing_source.json":
                del json_ld["@context"]["source"]
            json.dump(json_ld, f, indent="  ")
            f.write("\n")
    print("Done.")


if __name__ == "__main__":
    app.run(main)
