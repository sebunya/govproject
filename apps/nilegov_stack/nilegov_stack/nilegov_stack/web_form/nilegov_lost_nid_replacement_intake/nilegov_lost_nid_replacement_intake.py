# -*- coding: utf-8 -*-
# Copyright (c) 2026, Digi-Verse Uganda Limited
# License: MIT. See LICENSE

import frappe


def get_context(context):
    # Disable sidebar for clean public-facing intake layout
    context.show_sidebar = False
