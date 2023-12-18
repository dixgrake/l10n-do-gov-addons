# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools.translate import _

class FleetMethodPayment(models.Model):
        _name = 'fleet.method.payment'
        _inherit = ['mail.thread', 'mail.activity.mixin']
        _description = 'Record Method Payment'
        
        _sql_constraints = [('number_uniq', 'unique (account_number)', 'This account number already exists!')]

        ACCOUNT_TYPE_SELECTION = [
        ('credit', 'Tarjeta de Credito'),
        ('debit', 'Tarjeta de Debito'),
        ('current', 'Cuenta Corriente'),
        ('savings', 'Cuenta de Ahorro')
    ]

        name = fields.Char(string='Name', translate=True, compute='_compute_name', store=True)
        account_type = fields.Selection(ACCOUNT_TYPE_SELECTION, 
                                        'Account Type', 
                                        required=True, 
                                        tracking=True, 
                                        help='Choose if the type of account is a card, it can be a debit or credit type and if it is a savings or checking account.'
                                        )
        account_number = fields.Char(string='Account Number', required=True, tracking=True)
        bank_id = fields.Many2one('res.bank', string='Bank')
        cutoff_date = fields.Integer('Cutting day', required=True, tracking=True, help='Enter the day of the month (1-31)')
        due_date = fields.Char(string='Due Date', required=True, tracking=True)
        state = fields.Selection([
                ('new', 'New'),
                ('active', 'Active'),
                ('expired', 'Expired'),
                ('cancel', 'Cancelled'),
                ], string='Status', default='new', tracking=True)
        
        def action_set_active(self):
                self.write({'state': 'active'})

        def action_set_cancel(self):
                self.write({'state': 'cancel'})

        @api.onchange('account_type')
        def _onchange_account_type(self):
                if self.account_type in ['credit', 'debit','current','savings'] and not self.account_number:
                        raise ValidationError("The account number cannot be empty.")

        @api.depends('account_number', 'account_type')
        def _compute_name(self):
                for record in self:
                        if record.account_type in ['credit', 'debit']:
                                last_six_digits = record.account_number[-6:] if record.account_number else ''
                                account_type_label = dict(self._fields['account_type'].selection).get(record.account_type)
                                record.name = f"{account_type_label} - {last_six_digits}"
                        elif record.account_type in ['current', 'savings']:
                                record.name = record.account_number                               
                        else:
                                record.name = record.account_number

        @api.constrains('account_number', 'account_type')
        def _check_account_number_length(self):
                for record in self:
                        if record.account_type in ['credit', 'debit'] and len(record.account_number) !=16:
                                raise ValidationError('For credit and debit cards, the account number must be 16 characters long.')

        @api.constrains('due_date')
        def _check_due_date_format(self):
                for record in self:
                        if record.due_date:
                                self._validate_date_format(record.due_date)

        @staticmethod
        def _validate_date_format(date):
                """Validate date format <MM/YYYY>"""
                if date is not None:
                        error = _('Error. Date format must be MM/YYYY')
                        if len(date) == 7:
                                try:
                                        datetime.strptime(date, '%m/%Y')
                                except ValueError:
                                        raise ValidationError(error)
                        else:
                                raise ValidationError(error)