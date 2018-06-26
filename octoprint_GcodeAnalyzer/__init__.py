# coding=utf-8
from __future__ import absolute_import
from octoprint.filemanager.analysis import AbstractAnalysisQueue
from octoprint.filemanager.analysis import GcodeAnalysisQueue

import octoprint.plugin
import analyze_slic3r

class FileCommentGcodeAnalysisQueue(GcodeAnalysisQueue):
  """Extracts gcode analysis from the comments in the code."""

  def _do_analysis(self, high_priority=False):
    self._logger.info("GcodeAnalyzer starting on {}".format(self._current.absolute_path))
    ret = analyze_slic3r.get_analysis_from_gcode(self._current.absolute_path)
    if not ret: # Fallback to GcodeAnalysisQueue
      self._logger.info("GcodeAnalyzer found no results")
      ret = super(FileCommentGcodeAnalysisQueue, self)._do_analysis(high_priority)
    self._logger.info("GcodeAnalyzer results {}".format(ret))
    return ret


class GcodeAnalyzerPlugin(octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.RestartNeedingPlugin):

  ##~~ Gcode Analysis Hook
  def custom_gcode_analysis_queue(self, *args, **kwargs):
    return dict(gcode=FileCommentGcodeAnalysisQueue)

  ##~~ Softwareupdate hook
  def get_update_information(self):
    # Define the configuration for your plugin to use with the Software Update
    # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
    # for details.
    return dict(
        GcodeAnalyzer=dict(
            displayName="Gcodeanalyzer Plugin",
            displayVersion=self._plugin_version,

            # version check: github repository
            type="github_release",
            user="eyal0",
            repo="OctoPrint-GcodeAnalyzer",
            current=self._plugin_version,

            # update method: pip
            pip="https://github.com/eyal0/OctoPrint-GcodeAnalyzer/archive/{target_version}.zip"
        )
    )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "GcodeAnalyzer Plugin"

def __plugin_load__():
  global __plugin_implementation__
  __plugin_implementation__ = GcodeAnalyzerPlugin()

  global __plugin_hooks__
  __plugin_hooks__ = {
      "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
      "octoprint.filemanager.analysis.factory": __plugin_implementation__.custom_gcode_analysis_queue
  }
