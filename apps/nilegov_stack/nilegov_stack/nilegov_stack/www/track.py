# -*- coding: utf-8 -*-
# Copyright (c) 2026, Digi-Verse Uganda Limited
# License: MIT. See LICENSE

import frappe


def get_context(context):
    # Public route needs sidebar hidden
    context.show_sidebar = False
