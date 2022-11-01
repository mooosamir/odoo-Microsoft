# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from base64 import b32encode, b64encode
from os import remove, urandom
from tempfile import mkstemp
from logging import getLogger
from datetime import date,datetime
from contextlib import suppress

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.http import request
from random import randint
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
_logger = getLogger(__name__)
try:
    import twilio

except ImportError as error:
    _logger.debug(error)
from twilio.rest import Client

from ..exceptions import MissingOtpError, InvalidOtpError

_logger = getLogger(__name__)

try:
    import pyotp
    import qrcode

except ImportError as error:
    _logger.debug(error)


class OtpClass(models.Model):
    _name = 'otp.class'

    otp = fields.Char("Otp")
    user_id = fields.Many2one("res.users")
    mobile = fields.Char("Mobile No.")


class ResUsers(models.Model):
    _inherit = "res.users"

    enable_2fa = fields.Boolean(
        string="Two Factor Authentication",
        inverse="_inverse_enable_2fa",
    )
    secret_code_2fa = fields.Char(
        string="Two Factor Authentication Secret Code",
        copy=False,
    )
    qr_image_2fa = fields.Binary(
        string="Two Factor Authentication QR Code",
        copy=False,
    )
    mobile = fields.Char("Mobile No.")

    def generate_otp(self):
        otp_obj = self.env['otp.class'].sudo()
        otp = False
        otp_exist = otp_obj.search([('user_id', '=', self.id)])
        if otp_exist:
            create_date = datetime.strptime(str(otp_exist.create_date)[:19], '%Y-%m-%d %H:%M:%S')
            current_date = datetime.now()
            c = (current_date - create_date)
            minutes = c.seconds / 60
            if minutes > 2:
                otp_exist.unlink()
                otp = randint(1000, 9999)
                otp_record = otp_obj.create({'user_id': self.id, 'otp': otp, 'mobile': self.mobile})
                return {'mobile': self.mobile, 'otp': otp_record.otp, 'email': self.login}
            else:
                return {'mobile': self.mobile, 'otp': otp_exist.otp, 'email': self.login}
        else:
            otp = randint(1000, 9999)
            otp_record = otp_obj.create({'user_id': self.id, 'otp': otp, 'mobile': self.mobile})
            return {'mobile': self.mobile, 'otp': otp_record.otp, 'email': self.login}
        #return opt_record

    def _inverse_enable_2fa(self):
        """
        Inverse `enable_2fa` - call `action_discard_2f_auth_credentials` method
        if value of the field become `false`
        """
        for user in self:
            if not user.enable_2fa:
                user.action_discard_2f_auth_credentials()

    def action_discard_2f_auth_credentials(self):
        """
        Remove values from fields `qr_image_2fa`, `auth_secret_code_2fa`.
        This method calling when value of the field `enable_2fa` become `false`.
        Field `enable_2fa` can be changed only after checking rights for this action
        in method `write` and no need to check rights for
        `action_discard_2f_auth_credentials`.
        """
        values = {
            "qr_image_2fa": False,
            "secret_code_2fa": False,
        }
        self.write(values)

    def action_disable_2f_auth(self):
        """
        Set `enable_2fa` field value to `False`.
        """
        values = {
            "enable_2fa": False,
        }
        self.write(values)

    def action_enable_2f_auth(self):
        """
        Set `enable_2fa` field value to `False`.
        """
        values = {
            "enable_2fa": True,
        }
        self.write(values)

    def _check_credentials(self, password):
        """
        Overload core method to also check Two Factor Authentication credentials.
        Raises:
         * odoo.addons.two_factor_otp_auth.exceptions.MissingOtpError - no
            `otp_code` in request params. Should be caught by controller and
            render and open enter "one-time-password" page or QR code creation
        """
        super(ResUsers, self)._check_credentials(password)
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if self.id not in [1,2]:
            if self.enable_2fa or ICPSudo.get_param('global_send'):
                params = request.params
                #params.update({'otp_code': 123456})
                secret_code = self.secret_code_2fa or params.get("secret_code_2fa")
                if params.get("otp_code") is None:
                    request.session.otk_uid = self.id
                    raise MissingOtpError()
                else:
                    _logger.info("############ ------ %s"%(self.id))
                    otp_exist = self.env['otp.class'].sudo().search([('user_id', '=', self.id)])
                    create_date = datetime.strptime(str(otp_exist.create_date)[:19], '%Y-%m-%d %H:%M:%S')
                    current_date = datetime.now()
                    c = (current_date - create_date)
                    minutes = c.seconds / 60
                    if minutes > 2:
                        raise InvalidOtpError()
                    # can trigger `InvalidOtpError
                    self._check_otp_code(
                        otp_exist.otp,
                        params.pop("otp_code"),
                        secret_code,
                    )

    def _generate_secrets(self):
        """
        Generate QR-Code based on random set of letters
        Returns:
         * tuple - generated secret_code and binary qr-code
        """
        self.ensure_one()
        key = b32encode(urandom(10))
        # code = pyotp.totp.TOTP(key).provisioning_uri(self.login)
        # img = qrcode.make(code)
        # _, file_path = mkstemp()  # creating temporary file
        # img.save(file_path)

        # with open(file_path, "rb") as image_file:
        #     qr_image_code = b64encode(image_file.read())

        # # removing temporary file
        # with suppress(OSError):
        #     remove(file_path)
        qr_image_code = '2AFAFA'
        return key, qr_image_code

    @staticmethod
    def _can_change_2f_auth_settings(user):
        """
        Checking that user can make mass actions with 2FA settings.
        Argument:
        * user - `res.users` object
        Raises:
         * odoo.exceptions.AccessError: only users with `Mass Change 2FA Configuration
          for Users` rights can do this action
        """
        if not user.has_group("two_factor_otp_auth.mass_change_2fa_for_users"):
            raise AccessError(_(
                "Only users with 'Mass Change 2FA Configuration "
                "for Users' rights can do this operation!"
            ))

    @staticmethod
    def _check_otp_code(old_otp, otp, secret):
        """
        Validate incoming one time password `otp` witch secret via `pyotp`
        library methods.
        Args:
         * otp(str/integer) - one time password
         * secret(str) - origin secret of QR Code for one time password
           generator
        Raises:
         * odoo.addons.two_factor_otp_auth.exceptions.InvalidOtpError -
            one-time-password. Should be caught by controller and return user
            to enter "one-time-password" page
        Returns:
         * bool - True
        """
        # totp = pyotp.TOTP(secret)
        # str_otp = str(otp)
        # verify = totp.verify(str_otp)
        if old_otp != otp:
            raise InvalidOtpError()
        return True

    def send_sms(self, kw):
        #try:
        ICPSudo = self.env['ir.config_parameter'].sudo()
        account_sid = ICPSudo.get_param('account_sid')
        account_token = ICPSudo.get_param('account_token')
        from_mobile = ICPSudo.get_param('from_mobile')
        if account_sid and account_token and from_mobile and kw.get('mobile'):
            response_dict = {}
            client = Client(account_sid, account_token)
            response = client.messages.create(
                body="%s"%(kw.get('otp')),
                to="%s"%(kw.get('mobile')),
                from_="%s"%(from_mobile)
            )
            if response.sid:
                return True

    def body_html(self, otp):
        html = """
            <tbody>
                <tr>
                  <td>
                    <table cellspacing="0" cellpadding="0">
                      <tbody>
                      <tr>
                        <td>
                          <table cellspacing="0" cellpadding="0">
                            <tbody>
                            <tr>
                              <td width="250" valign="top" align="right"><p>Password assistance</p></td>
                            </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>

                      <tr>
                        <td>
                          <p>To authenticate, please use the following One Time Password (OTP):</p>
                          <p>%s</p>
                        </td>
                      </tr>

                      <tr>
                        <td>
                          <p>Do not share this OTP with anyone.It takes your account security very seriously.Customer Service will never ask you to disclose or verify your password, OTP, credit card, or banking account number. If you receive a suspicious email with a link to update your account information, do not click on the link—instead, report the email for investigation.

                          </p>
                        </td>
                      </tr>

                      <tr>
                        <td>
                          <p>We hope to see you again soon.
                          </p>
                        </td>
                      </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
                </tbody>
        """%(otp)
        return html

    def send_email(self, kw):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('two_factor_otp_auth', 'user_email_template_otp_mobile')[1]
            if template_id:
                ICPSudo = self.env['ir.config_parameter'].sudo()
                api_email_key = ICPSudo.get_param('api_email_key')
                vals = {'apikey':api_email_key}
                template = self.env['mail.template'].sudo().browse(template_id)
                mail_from = '%s'%(str(ICPSudo.get_param('email_from')))
                mail_to = '%s'%(str(kw.get('email')))
                msg = MIMEMultipart()
                msg['From'] = str(mail_from)
                msg['To'] = str(mail_to)
                msg['Subject'] =  template.subject
                mail_body = self.body_html(kw.get('otp'))
                part2 = MIMEText(mail_body, "html")
                msg.attach(part2)
                server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
                server.ehlo()
                server.login('apikey', vals.get('apikey')) #'%s')%(self.api_email_key)
                server.sendmail(mail_from, mail_to, msg.as_string())
                server.close()
                _logger.info("Message Send::")

        except Exception as e:
            _logger.info("Exception::%s"%(e))

    def generate_code(self, login):
        user_obj = self.env['res.users'].sudo()
        user_id = user_obj.search([('login', '=', login)])
        otp_obj = self.env['otp.class'].sudo()
        otp = False
        mobile = ''
        otp_exist = otp_obj.search([('user_id', '=', user_id.id)])
        if otp_exist:
            otp_exist.unlink()
            otp = randint(1000, 9999)
            otp_record = otp_obj.create({'user_id': user_id.id, 'otp': otp, 'mobile': user_id.mobile})
            mobile = user_id.mobile
        else:
            otp = randint(1000, 9999)
            otp_record = otp_obj.create({'user_id': user_id.id, 'otp': otp, 'mobile': user_id.mobile})
            mobile = user_id.mobile
        vals = {'otp': otp, 'mobile': mobile, 'email': user_id.login}
        self.send_sms(vals)
        self.send_email(vals)

    def delete_code(self, login):
        user_obj = self.env['res.users'].sudo()
        user_id = user_obj.search([('login', '=', login)])
        otp_obj = self.env['otp.class'].sudo()
        otp = False
        mobile = ''
        otp_exist = otp_obj.search([('user_id', '=', user_id.id)])
        if otp_exist:
            otp_exist.unlink()