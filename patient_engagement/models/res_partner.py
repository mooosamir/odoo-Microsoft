# -*- coding: utf-8 -*-

import os
import time
import pytz
import logging
import operator
from typing import re
from dateutil import tz
from twilio.rest import Client
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from dateutil.relativedelta import relativedelta

from odoo.osv.expression import select_from_where
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException
from ...opt_custom import models as timestamp_UTC


class ResPartner(models.Model):
    _inherit = 'res.partner'
    # _order = "create_date DESC"

    is_archived = fields.Boolean(default=False)