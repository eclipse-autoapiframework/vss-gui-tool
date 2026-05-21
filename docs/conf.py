# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
#   Thomas Pfleiderer - first documentation
# *******************************************************************************

# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html     


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Eclipse VSS GUI Tool"
project_url = "https://eclipse-autoapiframework.github.io/vss-gui-tool/"
project_prefix = "AUTOAPIFRAMEWORK_"
author = "Eclipse Automotive API Framework Contributors"
version = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "sphinx_design",
    "sphinx_needs",
    "sphinxcontrib.plantuml",
    "score_plantuml",
    "score_metamodel",
    "score_draw_uml_funcs",
    "score_source_code_linker",
    "score_layout",
]

templates_path = ["templates"]

# Enable numref
numfig = True

# Override S-CORE options for the theme
def override_theme_options(app, config):
    config.html_theme_options = {
        "logo": {"text": "Eclipse Automotive API Framework"},
        "logo_link": "index.html",
    }   

    config.html_static_path.append("_override_assets")
    config.html_css_files.append("css/custom.css")


def setup(app):
    app.connect("config-inited", override_theme_options)
