from common.utils import app_base_config, sidebar_config
from pages.pages import app_pages


def main():
    app_base_config()
    sidebar_config(app_pages())


if __name__ == "__main__":
    main()
