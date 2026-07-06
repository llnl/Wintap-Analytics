from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="EDA_",
    settings_files=["eda_settings.toml"],
)
