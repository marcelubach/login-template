import imp
import os

import logging

""" Plugin handler.
"""

PLUGIN_FOLDER = "./plugins"

class PluginHandler():
  isPluginLoaded = False
  # def __init__(self):
        # self.isPluginLoaded = False

  @classmethod
  def load(self):
    if self.isPluginLoaded:
      return
    self.isPluginLoaded = True
    possibleplugins = os.listdir(PLUGIN_FOLDER)
    for i in possibleplugins:
      # location = os.path.join(PLUGIN_FOLDER, i)
      if i[-3:] == ".py":
        moduleName = i[:-3]
        info = imp.find_module(moduleName, [PLUGIN_FOLDER])
        imp.load_module(moduleName, *info)
