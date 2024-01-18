from datetime import datetime
import pytz
from email.policy import default
import string
from warnings import WarningMessage
from xml.parsers.expat import model
from odoo import api, fields, models
from odoo.osv import expression
from odoo.exceptions import ValidationError


class Images(models.Model):
    _name = 'rapidusa.images'
    _description = 'Photos'

    transfer_related = fields.Many2one(related='record.rapiddriver_id')
    record = fields.Many2one('rapidusa.rapid_car', invisible=True)
    image = fields.Binary('Image')
    descrip = fields.Char('Notes')


class Driver(models.Model):
    _inherit = 'hr.employee'

    rapid_car_ids = fields.One2many('rapidusa.rapid_car', 'driver_id', string='Record')


class RapidCar(models.Model):
    _name = 'rapidusa.rapid_car'
    _description = 'Car Information'
    _order = 'rapiddriver_id desc'

    chapa = fields.Char('Plate No.')
    chapa_foto = fields.Binary('Plate')
    driver_id = fields.Many2one('hr.employee', 'Driver', required=True)
    millas_start = fields.Float('Initial Mileage')
    millas_fin = fields.Float('Final Mileage')
    millas_total = fields.Float('Miles Driven', compute='_compute_millas', store=True)
    rapiddriver_id = fields.Many2one('rapidusa.rapid_driver', 'Lot num', invisible=True)

    evidence = fields.One2many('rapidusa.images', 'record', string='Evidences')

    route_id_rel = fields.Many2one(related='rapiddriver_id.route_id')

    @api.depends('millas_start', 'millas_fin', 'millas_total')
    def _compute_millas(self):
        for i in self:
            if i.millas_fin != 0:
                i.millas_total = i.millas_fin - i.millas_start
            else:
                i.millas_total = 0


class Dispatch(models.Model):
    _name = 'rapidusa.dispatch'
    _description = 'Authorized Person to Dispatch'
    _rec_name = 'name'
    name = fields.Char('Name')


class RapidDriver(models.Model):
    _name = 'rapidusa.rapid_driver'
    _description = 'List of Vehicles in Transfer'
    _rec_name = 'transfer_id'

    transfer_id = fields.Char('Id', readonly=True)
    dispatcher_id = fields.Many2one('rapidusa.dispatch', 'Order Dispatched by', required=True)
    route_id = fields.Many2one('rapidusa.rapid_driver_fees', required=True)
    cr_date = fields.Date('Date', default=lambda self: datetime.now(pytz.timezone("US/Eastern")),
                          required=True)
    start_time = fields.Datetime('Start Time', readonly=True)
    end_time = fields.Datetime('End Time', readonly=True)
    trayecto_hrs = fields.Char(string='Time', readonly=True)
    cars_total = fields.Integer('Vehicles Moved', compute='_compute_cars_total', store=True)
    status = fields.Selection([('To_Go', 'To Go'),
                               ('Road', 'Running'),
                               ('Arrived', 'Arrived'),
                               ], string='Status', default='To_Go'
                              )
    rapidcar_ids = fields.One2many('rapidusa.rapid_car', 'rapiddriver_id', ondelete='cascade')
    fees_related = fields.Float('Fees', compute='_compute_fees', store=True)

    acc_status = fields.Selection([('Paid', 'Paid'),
                                   ('Billed', 'Billed'),
                                   ('Draft', 'Draft')], default='Draft')
    date_billed = fields.Date('Billed Date')
    date_paid = fields.Date('Paid Date')
    import_bol = fields.Boolean('Import', default=False)
    seq_no = fields.Char('Seq_No')

    def do_status_bill(self):
        for i in self:
            i.acc_status = 'Billed'
            i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
            i.date_paid = False

    def do_status_pay(self):
        for i in self:
            i.acc_status = 'Paid'
            i.date_paid = datetime.now(pytz.timezone("US/Eastern"))

    def do_status_next(self):
        for i in self:
            if i.acc_status == 'Draft':
                i.acc_status = 'Billed'
                i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
                break
            elif i.acc_status == 'Billed':
                i.acc_status = 'Paid'
                i.date_paid = datetime.now(pytz.timezone("US/Eastern"))
                break
            elif i.acc_status == 'Paid':
                raise ValidationError("You cannot change the Status")

    def do_status_back(self):
        for i in self:
            if i.acc_status == 'Paid':
                i.acc_status = 'Billed'
                i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
                i.date_paid = False
                break
            elif i.acc_status == 'Billed':
                i.acc_status = 'Draft'
                i.date_billed = False
                break
            elif i.acc_status == 'Draft':
                raise ValidationError("You cannot change the Status")

    @api.depends('rapidcar_ids', 'fees_related', 'route_id')
    def _compute_fees(self):

        self.fees_related = self.cars_total * self.route_id.fee

    @api.depends('rapidcar_ids', 'cars_total')
    def _compute_cars_total(self):
        total = 0
        for i in self:
            total = len(i.rapidcar_ids)
            # for j in i.rapidcar_ids:
            #     total += 1
        self.cars_total = total

    @api.model
    def create(self, vals):
        # if vals['import_bol'] and vals['seq_no']:
        #     vals['transfer_id'] = vals['seq_no']
        # else:
        #     seq = self.env['ir.sequence'].next_by_code('rapid_driver') or '/'
        #     vals['transfer_id'] = seq
        seq = self.env['ir.sequence'].next_by_code('rapid_driver') or '/'
        vals['transfer_id'] = seq
        return super(RapidDriver, self).create(vals)

    def unlink(self):
        for i in self:
            for j in i.rapidcar_ids:
                j.unlink()
        super(RapidDriver, self).unlink()

    def do_status_go(self):
        for i in self:
            if i.status == 'To_Go':
                i.status = 'Road'
                i.start_time = datetime.today()
            else:
                raise ValidationError('Wrong Status Sequence')

    def do_status_end(self):
        for i in self:
            if i.status == 'Road':
                i.status = 'Arrived'

                i.end_time = datetime.today()
                i.trayecto_hrs = i.end_time - i.start_time
            else:
                raise ValidationError('Wrong Status Sequence, your lot  has to be Running.' 'Actual State:' + i.status)


class RapidDriverFees(models.Model):
    _name = 'rapidusa.rapid_driver_fees'
    _description = 'Relation of Fees for vehicle Transfer'
    _rec_name = 'route_name'

    route_name = fields.Char('Route', compute="_compute_route_name", store=True)
    transfer_from = fields.Many2one('rapidusa.destino', 'From')
    transfer_to = fields.Many2one('rapidusa.destino', 'To')
    fee = fields.Float('Fee')

    @api.depends('transfer_from', 'transfer_to', 'route_name')
    def _compute_route_name(self):
        for i in self:
            seq = str(i.transfer_from.nombre_destino) + ' to ' + str(i.transfer_to.nombre_destino)
            i.route_name = seq


class Destino(models.Model):
    _name = 'rapidusa.destino'
    _description = 'Ubicaciones Destinos'
    _rec_name = 'nombre_destino'

    nombre_destino = fields.Char('Name')
    direccion = fields.Char('Address')
