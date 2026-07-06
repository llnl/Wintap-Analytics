# DataQA

Welcome to your Streamlit Application for Wintap Data: DataQA!

This template has the following features builtin:

* Multi-page support
* Wintap database selection
    * Specifically supports duckdb databases defined in [dataset_path]/[dataset]/dbhelpers
    * Once selected, database is available vi dqautil.getcon() on any page

## Initial Configuration
* Update contents of ```DataQA_settings.toml```

## Running your application

From this directory: ```streamlit run main.py```

At this point, it will run, but doesn't do much of anything but open the database and display a simple summary.

## Adding another page

1. Add a new page to the `pages/` directory
2. Ensure it implements a `__main__` function (use the example in `initial_page.py`)
3. Add it to the navigation in `utils/utils.py`
