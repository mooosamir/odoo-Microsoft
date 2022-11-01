# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import stripe
import datetime
import json


class PostSaleTransactions(http.Controller):
    @http.route('/stripe/set', type='http', auth='user', methods=['POST', 'GET'], csrf=False)
    def set(self, **kw):
        account_payment = request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')])
        account_payment.module_state = 'installed'
        return "OK"

    @http.route('/stripe/spk', type='http', auth='user', methods=['GET'])
    def key(self, **kw):
        return request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')]).stripe_backend_publishable_key
        open_session = request.env['sale.order.session'].search([("state", 'in', ['in_progress'])])
        total_sale = sum(request.env['sale.order'].search([('sale_order_session_id', '=', open_session.id)]).mapped('amount_total'))
        invoice_payments_widgets = request.env['sale.order'].search([('sale_order_session_id', '=', open_session.id)]).mapped('invoice_payments_widget')
        total_payments = 0
        for invoice_payments_widget in invoice_payments_widgets:
            invoice_payments_widget = json.loads(invoice_payments_widget)
            total_payments += sum([x['amount'] for x in invoice_payments_widget['content']])
        difference = total_sale - total_payments

    @http.route('/stripe/return/pay', type='json', auth='user', methods=['POST'])
    def return_pay(self, **kw):
        intent = None
        jsonrequest = request.jsonrequest
        if 'id' not in jsonrequest and 'account_payment_id' not in jsonrequest:
            return {'error': "internal server error, all values not get"}
        else:
            multi_invoice_payment_id = request.env['multi.invoice.payment'].search([('id', '=', int(jsonrequest['id']))])
            account_payment_id = request.env['account.payment'].search([('id', '=', int(jsonrequest['account_payment_id']))])
            try:
                stripe.api_key = request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')]).stripe_backend_secret_key
                stripe.api_version = "2020-08-27"
                if multi_invoice_payment_id.so_cash >= account_payment_id.amount_remaining:
                    multi_invoice_payment_id.so_cash = account_payment_id.amount_remaining
                    multi_invoice_payment_id._onchange_so_cash
                    intent = stripe.Refund.create(payment_intent=account_payment_id.payment_transaction_id.acquirer_reference,
                                                  amount=int("".join(multi_invoice_payment_id.so_cash.__format__('.2f').split('.'))))
                elif multi_invoice_payment_id.so_cash < account_payment_id.amount_remaining:
                    # multi_invoice_payment_id.so_cash = account_payment_id.amount
                    # multi_invoice_payment_id._onchange_so_cash
                    intent = stripe.Refund.create(payment_intent=account_payment_id.payment_transaction_id.acquirer_reference,
                                                  amount=int("".join(multi_invoice_payment_id.so_cash.__format__('.2f').split('.'))))
            except stripe.error.CardError as e:
                # Display error on client
                return {'error': e.user_message}
            except Exception as e:
                # Display error on client
                return {'error': e.user_message}

            return self.generate_response(intent, int(jsonrequest['id']), int(jsonrequest['account_payment_id']))

    @http.route('/stripe/returns', type='http', auth='user', methods=['GET'])
    def returns(self, **kw):
        account_payment_ids = request.env['account.payment']
        # jsonrequest = request.jsonrequest
        if 'id' in kw:
            multi_invoice_payment_id = request.env['multi.invoice.payment'].search([
                ('id', '=', kw['id'])])
            if len(multi_invoice_payment_id.invoice_ids) == 1:
                communictaion = request.env['account.move'].search([('invoice_origin', '=', multi_invoice_payment_id.invoice_ids.invoice_origin)]).mapped('name')
                account_payment_ids = account_payment_ids.search([('communication', 'in', communictaion),
                                                                          ('journal_id', '=', 'Stripe Backend')])
        # for account_payment_id in account_payment_ids:
        #     account_payments.append({
        #         'date': account_payment_id.payment_transaction_id.date,
        #         'memo': account_payment_id.communication,
        #         'amount': account_payment_id.amount,
        #         'acquirer_reference': account_payment_id.payment_transaction_id.acquirer_reference,
        #         'payment_transaction_id_amount': account_payment_id.payment_transaction_id.amount,
        #     })
        return request.render("post_sale_transactions.stripe_returns", {'account_payment_ids': account_payment_ids})

    @http.route('/stripe/pay', type='json', auth='user', methods=['POST'])
    def index(self, **kw):
        intent = None
        # "sk_test_51KC0crA8ZfvPg2oDxTuuMZlVHeYRG4lkiFktSNGiNanSJ9AGSBsKFPFggDRWjDAvAqjqjmtD8wryeSL4DIUCOEun00QzeCf9Ao"
        # 'pk_test_51KC0crA8ZfvPg2oDTfI9Vk6eC1HSnCICU3KV4g72sPCo0ftFISEa6P5ftYxDFLm2qnjmz5cDRIiZXQzTET5AeDWz00xe7jtsW6'
        stripe.api_key = request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')]).stripe_backend_secret_key
        stripe.api_version = "2020-08-27"
        jsonrequest = request.jsonrequest
        try:
            if 'payment_method_id' in jsonrequest:
                multi_invoice_payment_id = request.env['multi.invoice.payment'].search([
                    ('id', '=', jsonrequest['multi_invoice_payment_id'])])
                # Create the PaymentIntent
                customer = stripe.Customer.create(
                    # email=multi_invoice_payment_id.partner_id.email,
                    description="Payments for Sale Orders " + ",".join(multi_invoice_payment_id.invoice_lines.mapped(lambda x: x.sale_order_id.name)),
                    name=multi_invoice_payment_id.partner_id.display_name
                )

                intent = stripe.PaymentIntent.create(
                    customer=customer.id,
                    payment_method=jsonrequest['payment_method_id'],
                    amount=int("".join(multi_invoice_payment_id.so_cash.__format__('.2f').split('.'))),
                    currency=request.env.user.currency_id.display_name,
                    confirmation_method='manual',
                    confirm=True,
                    description="Payments for Sale Orders " + ",".join(multi_invoice_payment_id.invoice_lines.mapped(lambda x: x.sale_order_id.name)),
                    metadata={
                        'order_ids': ",".join(multi_invoice_payment_id.invoice_lines
                                              .mapped(lambda x: x.sale_order_id.name + "-" + str(x.amount) + "~")),
                    },
                )
            elif 'payment_intent_id' in jsonrequest:
                intent = stripe.PaymentIntent.confirm(jsonrequest['payment_intent_id'])
        except stripe.error.CardError as e:
            # Display error on client
            return {'error': e.user_message}
        except Exception as e:
            # Display error on client
            return {'error': e.user_message}

        return self.generate_response(intent, jsonrequest['multi_invoice_payment_id'])

    def generate_response(intents, intent, multi_invoice_payment_id, account_payment_id=0):
        # Note that if your API version is before 2019-02-11, 'requires_action'
        # appears as 'requires_source_action'.
        if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
            # Tell the client to handle the action
            return {
                'requires_action': True,
                'payment_intent_client_secret': intent.client_secret,
            }
        elif intent.status == 'succeeded':
            # The payment didn’t need any additional actions and completed!
            # Handle post-payment fulfillment
            try:
                multi_invoice_payment_id = request.env['multi.invoice.payment'].search([
                    ('id', '=', multi_invoice_payment_id)])

                if account_payment_id !=0:
                    account_payment_id = request.env['account.payment'].search([('id', '=', int(account_payment_id))])
                    account_payment_id.amount_remaining = account_payment_id.amount_remaining - multi_invoice_payment_id.so_cash
                    last4 = account_payment_id.payment_token_id.name[-4:]
                    brand = account_payment_id.payment_token_id.brand
                    customer = account_payment_id.payment_token_id.acquirer_ref
                if 'payment_method' in intent:
                    last4 = stripe.PaymentMethod.retrieve(intent.payment_method).card.last4
                    brand = stripe.PaymentMethod.retrieve(intent.payment_method).card.brand
                if 'customer' in intent:
                    customer = intent.customer
                payment_token_id = request.env['payment.token'].create({
                    'name': "XXXXXXXXXXXX" + last4,
                    'partner_id': multi_invoice_payment_id.partner_id.id,
                    'acquirer_id': request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')]).id,
                    'active': True,
                    'acquirer_ref': customer,
                    'brand': brand,
                })
                payment_transaction_id = request.env['payment.transaction'].create({
                    # 'payment_id': ,
                    'amount': multi_invoice_payment_id.so_cash.__format__('.2f'),
                    'partner_id': multi_invoice_payment_id.partner_id.id,
                    'acquirer_id': request.env['payment.acquirer'].search([('name', '=', 'Stripe Backend')]).id,
                    'acquirer_reference': intent.id,
                    'date': datetime.datetime.fromtimestamp(intent.created),
                    'payment_token_id': payment_token_id.id,
                    'invoice_ids': multi_invoice_payment_id.invoice_ids.ids,
                    'currency_id': request.env.user.currency_id.id,
                })
                multi_invoice_payment_id.create_payments(payment_transaction_id.id, payment_token_id.id)
            except Exception as e:
                return {'error': {
                            'type': "Internal Server Error",
                            'message': e,
                            'code': "",
                }}
            return {'success': True}
        else:
            # Invalid status
            return {'error': 'Invalid PaymentIntent status'}
