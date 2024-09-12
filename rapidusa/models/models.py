from datetime import datetime, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Images(models.Model):
    _name = "rapidusa.images"
    _description = "Photos"

    transfer_related = fields.Many2one(related="record.rapiddriver_id")
    record = fields.Many2one("rapidusa.rapid_car", invisible=True)
    image = fields.Binary("Image")
    descrip = fields.Char("Notes")


class Driver(models.Model):
    _inherit = "hr.employee"

    rapid_car_ids = fields.One2many("rapidusa.rapid_car", "driver_id", string="Record")


class RapidCar(models.Model):
    _name = "rapidusa.rapid_car"
    _description = "Car Information"
    _order = "rapiddriver_id desc"

    chapa = fields.Char("Plate No.")
    chapa_foto = fields.Binary("Plate")
    driver_id = fields.Many2one("hr.employee", "Driver")
    millas_start = fields.Float("Initial Mileage")
    millas_fin = fields.Float("Final Mileage")
    millas_total = fields.Float("Miles Driven", compute="_compute_millas", store=True)
    rapiddriver_id = fields.Many2one("rapidusa.rapid_driver", "Lot num", invisible=True)

    evidence = fields.One2many("rapidusa.images", "record", string="Evidences")

    route_id_rel = fields.Many2one(compute="_compute_route_id_rel", store=True)

    @api.depends("millas_start", "millas_fin", "millas_total")
    def _compute_millas(self):
        for i in self:
            if i.millas_fin != 0:
                i.millas_total = i.millas_fin - i.millas_start
            else:
                i.millas_total = 0

    @api.depends("rapiddriver_id")
    def _compute_route_id_rel(self):
        for i in self:
            if i.rapiddriver_id:
                if i.rapiddriver_id.route_id:
                    return i.rapiddriver_id.route_id
                else:
                    return i.rapiddriver_id.fees_service_id


class Dispatch(models.Model):
    _name = "rapidusa.dispatch"
    _description = "Authorized Person to Dispatch"
    _rec_name = "name"
    name = fields.Char("Name")
    employee_id = fields.Many2one("hr.employee", required=True)

    @api.onchange("employee_id")
    def _onchange_contact(self):
        if self.employee_id:
            self.name = self.employee_id.name


class RapidDriver(models.Model):
    _name = "rapidusa.rapid_driver"
    _description = "List of Vehicles in Transfer"
    _rec_name = "transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    transfer = fields.Char("Id", readonly=True)
    dispatcher_id = fields.Many2one("rapidusa.dispatch", "Order Dispatched by", required=True)
    route_id = fields.Many2one("rapidusa.rapid_driver_fees")
    fees_service_id = fields.Many2one("rapidusa.service_fees", "Service Fees")
    cr_date = fields.Date("Date", default=lambda self: datetime.now(pytz.timezone("US/Eastern")), required=True)
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    trayecto_hrs = fields.Float(string="Time / Hour", default=0)
    # trayecto_hrs_show = fields.Char(string="Time", default=0)
    cars_total = fields.Integer("Vehicles Moved", compute="_compute_cars_total", store=True)
    # status = fields.Selection([("To_Go", "To Go"),("Road", "Running"),("Arrived", "Arrived"),],string="Status",default="To_Go",)
    rapidcar_ids = fields.One2many("rapidusa.rapid_car", "rapiddriver_id")
    fees_related = fields.Float("Fees", compute="_compute_fees", store=True)
    acc_status = fields.Selection([("Draft", "Draft"), ("Billed", "Billed"), ("Paid", "Paid")], default="Draft")
    date_billed = fields.Date("Billed Date")
    date_paid = fields.Date("Paid Date")
    import_bol = fields.Boolean("Import", default=False)
    seq_no = fields.Char("Seq_No")
    customer_id = fields.Many2one("res.partner", string="Customer Invoices", domain="[('customer_rank' ,'>', 0)]", required=True)
    car_service_id = fields.Selection(
        [
            ("vehicle_transfers", "Vehicle Transfers"),
            ("car_wash_special_cleaner", "Car Wash (Special Cleaner)"),
            ("car_wash_regular_cleaner", "Car Wash (Regular Cleaner)"),
            ("drive_allocation", "Drive Allocation"),
        ],
        required=True,
        default="vehicle_transfers",
        string="Service",
        store=True,
    )
    reason_cleaning_ids = fields.Many2many("rapidusa.reason_cleaning")
    # workers_ids = fields.One2many("rapidusa.workers", "rapid_driver_id")
    # workers_total = fields.Integer("Workers Total", compute="_compute_workers_total", store=True)
    location_id = fields.Many2one("rapidusa.destino")
    move_count = fields.Integer(compute="_compute_move_count", string="Account Details")

    def _compute_move_count(self):
        for rapid_driver in self:
            line_count = self.env["account.move"].search([("payment_reference", "=", self.transfer)])
            rapid_driver.move_count = len(line_count)

    # def do_status_bill(self):
    #     for i in self:
    #         i.acc_status = "Billed"
    #         i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
    #         i.date_paid = False
    #
    # def do_status_pay(self):
    #     for i in self:
    #         i.acc_status = "Paid"
    #         i.date_paid = datetime.now(pytz.timezone("US/Eastern"))

    def do_status_next(self):
        for i in self:
            # if i.acc_status == "Paid":
            #     raise ValidationError("You cannot change the Status")
            # el
            if i.acc_status == "Draft":
                i.acc_status = "Billed"
                i.date_paid = datetime.now(pytz.timezone("US/Eastern"))
                break
            elif i.acc_status == "Billed":
                i.acc_status = "Paid"
                i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
                break

    # def do_status_back(self):
    #     for i in self:
    #         if i.acc_status == "Paid":
    #             i.acc_status = "Billed"
    #             i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
    #             i.date_paid = False
    #             break
    #         elif i.acc_status == "Billed":
    #             i.acc_status = "Draft"
    #             i.date_billed = False
    #             break
    #         elif i.acc_status == "Draft":
    #             raise ValidationError("You cannot change the Status")

    @api.depends("cars_total", "route_id", "fees_service_id")
    def _compute_fees(self):
        if self.car_service_id == "vehicle_transfers":
            self.fees_related = self.cars_total * self.route_id.fee
        else:
            self.fees_related = self.cars_total * self.fees_service_id.fee

    @api.depends("rapidcar_ids", "cars_total")
    def _compute_cars_total(self):
        total = 0
        for i in self:
            total = len(i.rapidcar_ids)
            # for j in i.rapidcar_ids:
            #     total += 1
        self.cars_total = total

    @api.model
    def create(self, vals_list):
        # if vals['import_bol'] and vals['seq_no']:
        #     vals['transfer_id'] = vals['seq_no']
        # else:
        #     seq = self.env['ir.sequence'].next_by_code('rapid_driver') or '/'
        #     vals['transfer_id'] = seq
        seq = self.env["ir.sequence"].next_by_code("rapid_driver") or "/"
        vals_list["transfer"] = seq
        return super(RapidDriver, self).create(vals_list)

    def unlink(self):
        for i in self:
            for j in i.rapidcar_ids:
                j.unlink()
        super(RapidDriver, self).unlink()

    def do_status_go(self):
        for i in self:
            i.start_time = datetime.today()

    def do_status_end(self):
        for i in self:
            i.end_time = datetime.today()

    @api.onchange("start_time", "end_time")
    def get_trayecto_hrs(self):
        for i in self:
            if i.end_time and i.start_time:
                aux = i.end_time - i.start_time
                minutes = aux.seconds / 60
                hours = minutes / 60 + aux.days * 24
                i.trayecto_hrs = round(hours, 2)
                # i.trayecto_hrs_show = str(aux)

    def write(self, vals):
        if self.trayecto_hrs < 0:
            raise ValidationError("Time / Hour must be end_time > start_time")
        if vals.get("acc_status"):
            if self.acc_status == "Paid" and not vals.get("acc_status") == "Paid":
                raise ValidationError("Can not change in state Paid.")
            if not (self.acc_status == "Billed") and vals.get("acc_status") == "Billed":
                self.generate_invoice()
        res = super(RapidDriver, self).write(vals)
        return res

    def generate_invoice(self):
        line_ids = []
        if self.car_service_id == "vehicle_transfers":
            fee = self.route_id.fee
        else:
            fee = self.fees_service_id.fee
        if self.car_service_id == "vehicle_transfers":
            product = self.env.ref("rapidusa.service_vehicle_transfers")
            line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": self.cars_total,
                        "name": product.name,
                        "price_unit": fee,
                    },
                )
            ]
        if self.car_service_id == "car_wash_special_cleaner":
            product = self.env.ref("rapidusa.service_car_wash_special_cleaner")
            line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": self.cars_total,
                        "name": product.name,
                        "price_unit": fee,
                    },
                )
            ]
        if self.car_service_id == "car_wash_regular_cleaner":
            product = self.env.ref("rapidusa.service_car_wash_regular_cleaner")
            line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": self.cars_total,
                        "name": product.name,
                        "price_unit": fee,
                    },
                )
            ]
        if self.car_service_id == "drive_allocation":
            product = self.env.ref("rapidusa.service_drive_allocation")
            line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": self.cars_total,
                        "name": product.name,
                        "price_unit": fee,
                    },
                )
            ]
        self.env["account.move"].create(
            {
                "payment_reference": self.transfer,
                "rapid_driver_id": self.id,
                "dispatcher_id": self.dispatcher_id,
                "move_type": "out_invoice",
                "journal_id": self.env.company.id,
                "partner_id": self.customer_id.id,
                "invoice_date": self.cr_date,
                "date": datetime.today(),
                "invoice_date_due": datetime.today() + timedelta(days=31),
                "invoice_line_ids": line_ids,
            }
        )

    @api.onchange("car_service_id")
    def change_value_to_null(self):
        if self.car_service_id == "vehicle_transfers":
            self.location_id = False
        if self.car_service_id == "car_wash_special_cleaner" or self.car_service_id == "car_wash_regular_cleaner":
            self.route_id = False
        if self.car_service_id == "drive_allocation":
            self.route_id = False

    # @api.depends("workers_ids")
    # def _compute_workers_total(self):
    #     for i in self:
    #         i.workers_total = len(i.workers_ids)

    @api.onchange("acc_status")
    def _change_acc_status(self):
        for i in self:
            if i.acc_status == "Billed":
                i.date_billed = datetime.now(pytz.timezone("US/Eastern"))
                break
            elif i.acc_status == "Paid":
                i.date_paid = datetime.now(pytz.timezone("US/Eastern"))


class RapidDriverFees(models.Model):
    _name = "rapidusa.rapid_driver_fees"
    _description = "Relation of Fees for vehicle Transfer"
    _rec_name = "route_name"

    route_name = fields.Char("Route", compute="_compute_route_name", store=True)
    transfer_from = fields.Many2one("rapidusa.destino", "From")
    transfer_to = fields.Many2one("rapidusa.destino", "To")
    fee = fields.Float("Fee")

    @api.depends("transfer_from", "transfer_to", "route_name")
    def _compute_route_name(self):
        for i in self:
            seq = str(i.transfer_from.nombre_destino) + " to " + str(i.transfer_to.nombre_destino)
            i.route_name = seq


class Destino(models.Model):
    _name = "rapidusa.destino"
    _description = "Ubicaciones Destinos"
    _rec_name = "nombre_destino"

    nombre_destino = fields.Char("Name")
    direccion = fields.Char("Address")


class WorkerRole(models.Model):
    _name = "rapidusa.worker_role"
    _description = "Worker Role"

    name = fields.Char("Name", required=True)
    # fee = fields.Float("Fee",default=0, required=True)


class Workers(models.Model):
    _name = "rapidusa.workers"
    _description = "Workers"

    employee_id = fields.Many2one("hr.employee", required=True)
    worker_role_id = fields.Many2one("rapidusa.worker_role", required=True)
    rapid_attendances_id = fields.Many2one("rapidusa.attendances")


class ReasonCleaning(models.Model):
    _name = "rapidusa.reason_cleaning"
    _description = "Reason for Cleaning"

    name = fields.Char("Name")


class ServiceFees(models.Model):
    _name = "rapidusa.service_fees"
    _description = "Service Fees"

    name = fields.Char("Name", required=True)
    fee = fields.Float("Fee", default=0, required=True)
