import os
import logging
from src.GUI.settings import SettingsGUI
from src.utils import config

if __name__ == "__main__":
    try:
        SettingsGUI()
    except Exception as e:
        logging.exception(e)
    finally:
        if config.out and os.path.exists(config.out.output_dir):
            config.out.accdb.close_accdb()
        logging.info("Done!")
