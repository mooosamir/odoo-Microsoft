# -*- coding: utf-8 -*-

import os
import time
import pytz
from typing import re
from dateutil import tz
from twilio.rest import Client
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException


class LogsLog (models.Model):
    _name = 'logs.log'
    _order = "create_date DESC"

    log = fields.Text(string="Log")
    type = fields.Char(string="type")
