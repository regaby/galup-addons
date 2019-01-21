odoo.define('pos_einvoice_ar.PosModel', function(require){
"use strict";


    var models = require('point_of_sale.models');
    //var Model = require('web.Model');
    var Model = require('web.DataModel');
    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        push_and_invoice_order: function(order){
        var self = this;
        var invoiced = new $.Deferred();

        if(!order.get_client()){
            invoiced.reject({code:400, message:'Missing Customer', data:{}});
            return invoiced;
        }

        var order_id = this.db.add_order(order.export_as_JSON());

        this.flush_mutex.exec(function(){
            var done = new $.Deferred(); // holds the mutex

            // send the order to the server
            // we have a 30 seconds timeout on this push.
            // FIXME: if the server takes more than 30 seconds to accept the order,
            // the client will believe it wasn't successfully sent, and very bad
            // things will happen as a duplicate will be sent next time
            // so we must make sure the server detects and ignores duplicated orders

            var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});

            transfer.fail(function(error){
                invoiced.reject(error);
                done.reject();
            });

            // on success, get the order id generated by the server
            transfer.pipe(function(order_server_id){
                var records = new Model('pos.order')
                            .query(['invoice_id'])
                            .filter([['id', '=', order_server_id]])
                            .all()

                records.then(function(result){
                    var action = {
                        type: 'ir.actions.report.xml',
                        report_name: 'aeroo_report_ar_einvoice',
                        datas: {model:'account.invoice', id:ids[0], report_type:'aeroo', ids:ids},
                        context: {active_ids:ids, model:'account.invoice', ids:ids, active_model:'account.invoice',},
                        additional_context:{active_ids:ids[0]},
                    };
                    self.chrome.do_action(action)
                }
                );
                invoiced.resolve();
                done.resolve();
            });

            return done;

        });

        return invoiced;
    },
    });
});
