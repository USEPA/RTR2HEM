import os
import logging

from modules.GUI import SettingsGUI
from modules.utils import config

if __name__ == "__main__":
    try:
        SettingsGUI()
    except Exception as e:
        logging.exception(e)
        if config.out and os.path.exists(config.out.output_dir):
            config.out.accdb.close_accdb()
    finally:
        logging.info("Done!")
