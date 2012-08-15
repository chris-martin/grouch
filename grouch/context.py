import logging
import os

def makedirs(path):
  if not os.path.exists(path):
    os.makedirs(path)

def config_home():
  return os.getenv('XDG_CONFIG_HOME') \
      or ('%s/.config' % os.getenv('HOME'))

class Context:

  def __init__(self):
    self.init_config_dir()
    self.init_logger()

  def init_config_dir(self):
    self.__config_dir = '%s/grouch' % config_home()
    makedirs(self.__config_dir)

  def init_logger(self):

    logger = logging.getLogger(__name__)

    handler = logging.FileHandler(
      '%s/log' % self.__config_dir)

    formatter = logging.Formatter(
      '%(asctime)s %(levelname)s %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    self.__logger = logger

  def get_config_dir(self):
    return self.__config_dir

  def get_logger(self):
    return self.__logger
