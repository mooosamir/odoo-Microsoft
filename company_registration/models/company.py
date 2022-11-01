from odoo import models, fields, api


class CompanyRegistration(models.Model):
    _inherit = 'res.company'

    fax = fields.Char(string='Fax')
    npi = fields.Char(string='NPI')
    company_close_open_ids = fields.One2many('company.open.close',
                                             'company_id',
                                             string="Company Close/Open")
    facility_type = fields.Selection([('telehealth', '02-Telehealth'), ('school', '03-School'),
                                      ('india_fee_standin', '05-Indian Health Service Free-standin Facility'),
                                      ('india_provide_based', '06-Indian Health Service Provider-based Facility'),
                                      ('tribal_fee_standin', '07-Tribal 638 Free-standing Facility'),
                                      ('tribal_provide_based', '08-Tribal 638 Provider-based Facility'),
                                      ('prison_correctional_facility', '09-Prison/Correctional Facility'),
                                      ('office', '11-Office'),
                                      ('home', '12-Home'), ('assisted_living_facility', '13-Assisted Living Facility'),
                                      ('group_home', '14-Group Home'), ('mobile_unite', '15-Mobile Unit'),
                                      ('temporary_lodging', '16-Temporary Lodging'),
                                      ('health_clinick', '17-Walk-in Retail Health Clinic'),
                                      ('place_employment_works', '18-Place of Employment Worksite'),
                                      ('outpaatient_hospital', '19-Off Campus-Outpatient Hospital'),
                                      ('skilled_nursing_facility', '31-Skilled Nursing Facility'),
                                      ('nursing_facility', '32-Nursing Facility'),
                                      ('hospice', '34-Hospice'), ('comprehensive_inpatient_rehabilitation',
                                                                  '61-Comprehensive Inpatient Rehabilitation Facility'),
                                      ('comprehensive_outpatient_rehabilitation',
                                       '62-Comprehensive Outpatient Rehabilitation Facility'),
                                      ('other_place_service', '99-Other Place of Service')],
                                     string="Facility Type")
    location_code = fields.Char(string="Location Code")
    default_provider = fields.Many2one('hr.employee', string='Default Provider', domain=[('doctor','=',True)])
    clia = fields.Text(string='CLIA')
    claim_npi_entity = fields.Selection([('inidividual','Individual'),('organization','Organization')])
    clock_in = fields.Boolean(string='Clock in required')
    add_inventory = fields.Boolean(string='Add inventory to all locations')
    label_width = fields.Float(string="Label Width")
    label_height = fields.Float(string="Label Height")
    currency = fields.Many2one('res.currency',string='Currency')
    currency_position = fields.Selection([('before','Before'),('after','After')])
    barcode_type = fields.Selection([('code_39','Code 39'),('code_128','Code 128'),('interleaved','Interleaved 2 of 5'),('upc','UPC'),('ean','EAN'),('pdf417','PDF 417'),('data_matrix','Data Matrix'),('qr','QR')])
    barcode_width = fields.Float(string="Barcode Width")
    barcode_height = fields.Float(string="Barcode Height")
    integrated_label = fields.Many2one('default.label',string='Label')
    category_based_tax_id = fields.One2many('category.based.tax','company_field', string='')

    @api.model
    def default_get(self, fields_list):
        res = super(CompanyRegistration, self).default_get(fields_list)
        resObj = self.env['product.category'].search([])
        week = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        ml = []
        pc = []
        for day in week:
            ml.append((0, 0, {'day_select': day}))
        res['company_close_open_ids'] = ml

        for r in resObj:
            pc.append((0, 0, {'product_category': r.id}))
        res['category_based_tax_id'] = pc
        return res

    def write(self, vals):
        company = super(CompanyRegistration, self).write(vals)
        user_id = self.partner_id.user_id.search([('partner_id', '=', self.partner_id.id)])
        user_id.company_ids += self
        user_id.company_id = self.id
        # self.partner_id.company_id = self.id
        return company

    @api.model
    def create(self, values):
        company = super(CompanyRegistration, self).create(values)
        return company
