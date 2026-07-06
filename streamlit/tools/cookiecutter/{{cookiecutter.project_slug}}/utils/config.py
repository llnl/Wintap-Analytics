from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix='{{ cookiecutter.project_slug |replace(" ", "_")|upper }}_',
    settings_files=['{{cookiecutter.project_slug |replace(" ", "_")}}_settings.toml'],
)
