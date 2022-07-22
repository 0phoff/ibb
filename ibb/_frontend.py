#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 0phoff.
# Distributed under the terms of the Modified BSD License.

"""
Information about the frontend package of the widgets.
"""
from ._version import version_info

module_name = 'ibb'
module_version = '^' + '.'.join(map(str, version_info[:3]))
