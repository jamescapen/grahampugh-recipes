#!/usr/bin/python
#
# 2019 Graham R Pugh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for LastRecipeRunChecker class"""

import json
import os
import sys

import os.path
from autopkglib import Processor, ProcessorError  # pylint: disable=import-error


__all__ = ["LastRecipeRunChecker"]


class LastRecipeRunChecker(Processor):
    """An AutoPkg pre-processor which reads the output from the LastRecipeRunResult processor from a different AutoPkg recipe, so that they can be used in the foillowing processes."""

    input_variables = {
        "recipeoverride_identifier": {
            "description": "The identifier of the recipe from which the information is required.",
            "required": True,
        },
        "cache_dir": {
            "description": "Path to the cache dir.",
            "required": False,
            "default": "~/Library/AutoPkg/Cache",
        },
        "info_file": {
            "description": ("Name of inmput file."),
            "required": False,
            "default": "latest_version.json",
        },
    }

    output_variables = {
        "url": {"description": ("the download URL."),},
        "version": {"description": ("The current package version."),},
        "pkg_path": {"description": ("the package path."),},
        "pkg_name": {"description": ("the package name."),},
        "PKG_CATEGORY": {"description": ("The package category."),},
        "SELFSERVICE_DESCRIPTION": {"description": ("The self-service description."),},
    }

    description = __doc__

    def get_latest_recipe_run_info(self, cache_dir, identifier, info_file):
        """get information from the output files of a LastRecipeRunResult processor"""
        try:
            info_filepath = os.path.join(cache_dir, identifier, info_file)
            with open(info_filepath, "r") as fp:
                data = json.load(fp)
        except (IOError, ValueError):
            raise ProcessorError("No package or version information found")
        else:
            return data

    def main(self):
        identifier = self.env.get("recipeoverride_identifier")
        cache_dir = os.path.expanduser(self.env.get("cache_dir"))
        info_file = self.env.get("info_file")

        version_found = False

        # make sure all the values were obtained from the file
        data = self.get_latest_recipe_run_info(cache_dir, identifier, info_file)
        self.env["version"] = data["version"]
        self.env["pkg_name"] = data["pkg_name"]
        if not self.env["version"] or not self.env["pkg_name"]:
            raise ProcessorError("No package or version information found")
        self.env["pkg_path"] = data["pkg_path"]
        self.env["url"] = data["url"]
        self.env["PKG_CATEGORY"] = data["category"]
        self.env["SELFSERVICE_DESCRIPTION"] = data["self_service_description"]

        # make sure the package actually exists
        if not os.path.exists(self.env["pkg_path"]):
            raise ProcessorError(
                "Package does not exist: {}".format(self.env["pkg_path"])
            )

        self.output(f"Package name: {data['pkg_name']}")
        self.output(f"Package path: {data['pkg_path']}")
        self.output(f"Version: {data['version']}")
        self.output(f"URL: {data['url']}")
        self.output(f"Pkg Category: {data['category']}")
        self.output(f"Self Service Description: {data['self_service_description']}")


if __name__ == "__main__":
    PROCESSOR = LastRecipeRunChecker()
    PROCESSOR.execute_shell()
