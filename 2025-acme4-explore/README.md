# ACME4 Explore

This subdirectory hosts notebooks and code produced as part of the ACME4 Explore at-home research surge.
The goal is to progress in the exploratory analysis and auditing of the ACME4 host-based dataset,
in order to document its phenomena and properties,
and assess its utility for developing host-based cyber defense analytics.
We also expect the methods developed here to be useful in the exploratory analysis of other similar datasets
captured in context of organizations' own cyber defense missions.

## Getting started

The data processing and analysis built here is performed using Jupyter notebooks computed using Python.
The dependency stack and the project are wrangled using [**uv**](https://docs.astral.sh/uv/).
If you've never used uv, just go `pip install --user uv` and follow along.

### Running from your own computer

If you would compute using your own instance of Jupyter Lab, just before you do it *the first time after cloning the repo locally*,
run

```sh
uv run python -m ipykernel install --sys-prefix --name acme4-explore --display-name "ACME4 Explore"
```

Then, as usual, and every other time:

```sh
uv run jupyter lab  # With your favorite parameters
```

The one-time first step makes sure that all notebooks' kernel gets and remains named **ACME4 Explore**,
avoiding confusion for users that compute out of Jupyterhub servers.

### Running from a Jupyterhub server

Deploy the project as a kernel of your own:

```sh
uv run python -m ipykernel install --user --name acme4-explore --display-name "ACME4 Explore"
```

When then until the **ACME4 Explore** kernel shows in the Jupyter launcher,
then you can open the project's notebooks without Jupyter asking you to choose a kernel.

## Accessing the dataset

The ACME4 dataset is [published](https://gdo168.llnl.gov/) by the Lawrence Livermore National Laboratory.
It consists in various views of Wintap data collected in an ad hoc laboratory cloud environment over roughly one month.
This environment was used by some LLNL scientists to perform some of their work,
and was also visited by penetration testing professionals.
ACME4 Explore focuses on a more heavily engineered view of the data called the [*standard view*](https://gdo168.llnl.gov/data/ACME4/stdview-20240819-20240923/).
Under this perspective, the dataset is composed of a set of Parquet files,
each of which stores events of a specific type,
metadata about certain artifacts,
or labels attributed to events or processes.

A set of mutually related Parquet files such as this is efficiently wrangled using [DuckDB](https://duckdb.org/).
By default, we use its [HTTPFS](https://duckdb.org/docs/stable/core_extensions/httpfs/overview.html)
extension access the data directly from LLNL's webpage.
Each Parquet file can be added to a DuckDB database as a view.
The [`acme4-explore`](src/acme4-explore/) module included herein provides function `connect_db` to facilitate the construction of
the complete set of views.
Example (run in a Jupyter notebook):

```python
from acme4_explore import connect_db
conn = connect_db()  # Takes about 30 seconds to add all the views.
display(conn.sql("select table_name, table_type from information_schema.tables").df())
```

### Local dataset copy

Alternatively, the standard view can be [downloaded](https://gdo168.llnl.gov/data/ACME4/stdview-20240819-20240923.tar)
and perused locally.
One then simply appends to a `.env` file in the current subdirectory a definition such as
<a id="uri-dataset"></a>

```
URI_DATASET = "path/to/their/parquet/files"
```

This URI may either be a path on the local filesystem or a HTTP[S] URL
(for instance, to share the dataset among many workstations on a local network).
For example, let's say one extracts the Tar archive they downloaded from the link above to their home directory,
so that the Parquet files are stored in a directory at `$HOME/stdview-20240819-20240923`;
they had previously cloned this repository to `$HOME/Wintap-Analytics`
Then they append the following line to `$HOME/Wintap-Analytics/2025-acme4-explore/.env`:

```
URI_DATASET = "~/stdview-20240819-20240923"
```

Note that any environment variable can be dereferenced in this definition using the `${VAR}` syntax
(e.g. `URI_DATASET = "${HOME}/blah"`).

## Local configuration

This project uses [Dotenv](https://github.com/theskumar/python-dotenv) to manage configurable settings
(as hinted [previously](#Local-dataset-copy)).
These settings are sourced out of a file named `.env` living in this subproject directory.
The following table details the configurable settings for various tools included in the `acme4_explore` module:

| Variable | Explanation | Default value |
|----------|-------------|---------------|
| `DIR_WORK` | Directory in which intermediate artifacts are written. In particular, the database instance connected to by `connect_db` has persistent storage under the name `db` in this directory. | `./.work` |
| `URI_DATASET` | [Location](#uri-dataset) of the standard view Parquet files. Can be either a local filesystem path or a HTTP[S] URL. | https://gdo168.llnl.gov/data/ACME4/stdview-20240819-20240923/ |
| `LOGGING`     | JSON-encoded dictionary of parameters one would pass to `logging.basicConfig` to set up logging. | `{}` |
| `LOG_LEVEL`   | JSON-encoded dictionary that maps module names to specific logging levels. For instance, to debug `acme4_explore`, use `{"acme4_explore": "DEBUG"}`. | `{}` |
