from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DATAQA_",
    settings_files=["DataQA_settings.toml"],
)
