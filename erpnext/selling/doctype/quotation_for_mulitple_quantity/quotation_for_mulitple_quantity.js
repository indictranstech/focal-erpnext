cur_frm.cscript.tname = "Multiple Quantity Item";
cur_frm.cscript.fname = "multiple_quantity_item";
cur_frm.cscript.other_fname = "other_charges";
cur_frm.cscript.sales_team_fname = "sales_team";


{% include 'selling/sales_common.js' %}
{% include 'accounts/doctype/sales_taxes_and_charges_master/sales_taxes_and_charges_master.js' %}
{% include 'utilities/doctype/sms_control/sms_control.js' %}
{% include 'accounts/doctype/sales_invoice/pos.js' %}

cur_frm.add_fetch('item_code', 'part_number', 'part_number');
//cur_frm.add_fetch('item_code', 'item_name', 'item_name');

erpnext.selling.QuotationController = erpnext.selling.SellingController.extend({
	onload: function(doc, dt, dn) {
		var me = this;
		this._super(doc, dt, dn);
		if(doc.__islocal){
			get_server_fields('set_label','','',doc,dt,dn,1,function(r){refresh_field('multiple_quantity_item');
			 refresh_field(['quantity_lable','qty_label','t_lable','rq1','rq2','rq3']);
			 me.change_grid_labels()
			})
		}
	},
	refresh: function(doc, dt, dn) {
		this._super(doc, dt, dn);
		// console.log(cur_frm)
		if(doc.docstatus == 1 && doc.status!=='Lost') {
			cur_frm.add_custom_button(__('Make Sales Order'),
				cur_frm.cscript['Make Sales Order']);
			if(doc.status!=="Ordered") {
				cur_frm.add_custom_button(__('Set as Lost'),
					cur_frm.cscript['Declare Order Lost'], "icon-exclamation");
			}
			cur_frm.appframe.add_button(__('Send SMS'), cur_frm.cscript.send_sms, "icon-mobile-phone");
		}

		if (!doc.__islocal) {
			cur_frm.communication_view = new frappe.views.CommunicationList({
				list: frappe.get_list("Communication", {"parent": doc.name, "parenttype": "Quotation"}),
				parent: cur_frm.fields_dict.communication_html.wrapper,
				doc: doc,
				recipients: doc.contact_email
			});
		}
		this.toggle_reqd_lead_customer();
		if (!doc.__islocal && doc.docstatus!=1) {
			cur_frm.add_custom_button(__('Create RFQ for Material'), cur_frm.cscript.rfq_material, "icon-mobile-phone");
			cur_frm.add_custom_button(__('Create RFQ for PP'), cur_frm.cscript.rfq_pp, "icon-mobile-phone");
			cur_frm.add_custom_button(__('Create RFQ for SP'), cur_frm.cscript.rfq_sp, "icon-mobile-phone");
			cur_frm.add_custom_button(__('Create RFQ for SM'), cur_frm.cscript.rfq_sm, "icon-mobile-phone");
		}
	

	},

	quotation_to: function() {
		var me = this;
		if (this.frm.doc.quotation_to == "Lead") {
			this.frm.set_value("customer", null);
			this.frm.set_value("contact_person", null);
		} else if (this.frm.doc.quotation_to == "Customer") {
			this.frm.set_value("lead", null);
		}

		this.toggle_reqd_lead_customer();
	},

	toggle_reqd_lead_customer: function() {
		var me = this;

		this.frm.toggle_reqd("lead", this.frm.doc.quotation_to == "Lead");
		this.frm.toggle_reqd("customer", this.frm.doc.quotation_to == "Customer");

		// to overwrite the customer_filter trigger from queries.js
		$.each(["customer_address", "shipping_address_name"],
			function(i, opts) {
				me.frm.set_query(opts, me.frm.doc.quotation_to==="Lead"
					? erpnext.queries["lead_filter"] : erpnext.queries["customer_filter"]);
			}
		);
	},

	tc_name: function() {
		this.get_terms();
	},

	validate_company_and_party: function(party_field) {
			return this._super(party_field);
	},

	lead: function() {
		var me = this;
		frappe.call({
			method: "erpnext.selling.doctype.lead.lead.get_lead_details",
			args: { "lead": this.frm.doc.lead },
			callback: function(r) {
				if(r.message) {
					me.frm.updating_party_details = true;
					me.frm.set_value(r.message);
					me.frm.refresh();
					me.frm.updating_party_details = false;

				}
			}
		})
	},
	customer: function() {
		var me = this;
		frappe.call({
			method: "erpnext.selling.doctype.quotation.quotation.get_customer_refno",
			args: { "customer": this.frm.doc.customer },
			callback: function(r) {
				if(r.message) {
					me.frm.set_value("customer_ref_no", r.message[0][0])
					refresh_field('customer_ref_no');
				}
			}
		})
	},

	item_code:function(doc,cdt,cdn){
		var row = frappe.get_doc(cdt, cdn);
		get_server_fields('get_item_details',row.item_code,'',doc,cdt,cdn,1,function(r){
			refresh_field('multiple_quantity_item')	
		})
		
	},
	//anand
	change_grid_labels:function(doc,cdt,cdn){
		var me = this;
		var field_label_map = {};
		label_fields_c=me.frm.doc.quantity_lable
		label_fields_t=me.frm.doc.qty_label
		label_fields_t1=me.frm.doc.t_lable
		// label_fields_t1=1
		if (label_fields_c || label_fields_t || label_fields_t1){
			if (label_fields_c){
				label_dict_c=JSON.parse(label_fields_c)
			}
			if (label_fields_t){
				label_dict_t=JSON.parse(label_fields_t)	
			}
			if (label_fields_t1){
				label_dict_t1=JSON.parse(label_fields_t1)	
			}
			var setup_field_label_map_c = function(fields_list,parentfield) {
			var grid_doctype = me.frm.fields_dict[parentfield].grid.doctype;
				$.each(fields_list, function(i, fname) {
					var docfield = frappe.meta.docfield_map[grid_doctype][fname];
					if(docfield) {
						if (label_dict_c){
							var label = docfield.label='Qty '+label_dict_c[fname]
							field_label_map[grid_doctype + "-" + fname] =
							label.trim();
						}
					}
				});
			}
			var setup_field_label_map_t = function(fields_list,parentfield) {
			var grid_doctype = me.frm.fields_dict[parentfield].grid.doctype;
				$.each(fields_list, function(i, fname) {
					var docfield = frappe.meta.docfield_map[grid_doctype][fname];
					if(docfield) {
						if (label_dict_t){
							var label = docfield.label='Qty '+label_dict_t[fname]
							field_label_map[grid_doctype + "-" + fname] =
							label.trim();
						}
					}
				});
			}
			var setup_field_label_map_t1 = function(fields_list,parentfield) {
			var grid_doctype = me.frm.fields_dict[parentfield].grid.doctype;
				$.each(fields_list, function(i, fname) {
					var docfield = frappe.meta.docfield_map[grid_doctype][fname];
					if(docfield) {
						if (label_dict_t1){
							var label = docfield.label='Qty '+label_dict_t1[fname]
							field_label_map[grid_doctype + "-" + fname] =
							label.trim();
						}
					}
				});
			}
			setup_field_label_map_c(["r_qty1", "r_qty2", "r_qty3"],this.fname);
			setup_field_label_map_t(["r_qty_4", "r_qty_5", "r_qty_6"],this.fname);
			setup_field_label_map_t1(["r_qty_7", "r_qty_8", "r_qty_9"],this.fname);
			$.each(field_label_map, function(fname, label) {
				fname = fname.split("-");
				var df = frappe.meta.get_docfield(fname[0], fname[1], me.frm.doc.name);
				if(df) df.label = label;
			});
		}
		
	}
});

cur_frm.script_manager.make(erpnext.selling.QuotationController);

cur_frm.cscript['Make Sales Order'] = function() {
	frappe.model.open_mapped_doc({
		method: "erpnext.selling.doctype.quotation_for_mulitple_quantity.quotation_for_mulitple_quantity.make_sales_order",
		frm: cur_frm
	})
}

cur_frm.cscript['Declare Order Lost'] = function(){
	var dialog = new frappe.ui.Dialog({
		title: "Set as Lost",
		fields: [
			{"fieldtype": "Text", "label": __("Reason for losing"), "fieldname": "reason",
				"reqd": 1 },
			{"fieldtype": "Button", "label": __("Update"), "fieldname": "update"},
		]
	});

	dialog.fields_dict.update.$input.click(function() {
		args = dialog.get_values();
		if(!args) return;
		return cur_frm.call({
			method: "declare_order_lost",
			doc: cur_frm.doc,
			args: args.reason,
			callback: function(r) {
				if(r.exc) {
					msgprint(__("There were errors."));
					return;
				}
				dialog.hide();
				cur_frm.refresh();
			},
			btn: this
		})
	});
	dialog.show();

}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(frappe.boot.notification_settings.quotation))
		cur_frm.email_doc(frappe.boot.notification_settings.quotation_message);
}

cur_frm.fields_dict["multiple_quantity_item"].grid.get_field("raw_material_costing").get_query = function(doc) {
	return {
		query:"erpnext.selling.doctype.quotation.quotation.raw_material_costing_query",
		filters: {
			'from_quotation': doc.name
		}
	}
}
cur_frm.fields_dict["multiple_quantity_item"].grid.get_field("primary_process_costing").get_query = function(doc) {
	return {
		query:"erpnext.selling.doctype.quotation.quotation.primary_process_costing_query",
		filters: {
			'from_quotation': doc.name
		}
	}
}
cur_frm.fields_dict["multiple_quantity_item"].grid.get_field("secondary_process_costing").get_query = function(doc) {
	return {
		query:"erpnext.selling.doctype.quotation.quotation.secondary_process_costing_query",
		filters: {
			'from_quotation': doc.name
		}
	}
}
cur_frm.fields_dict["multiple_quantity_item"].grid.get_field("sub_machining_costing").get_query = function(doc) {
	return {
		query:"erpnext.selling.doctype.quotation.quotation.sub_machining_costing_query",
		filters: {
			'from_quotation': doc.name
		}
	}
}

//anand
cur_frm.cscript.raw_material_costing=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	if (d.raw_material_costing){
	return $c_obj(doc, 'get_rm_total_price', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
	}
}
//anand
cur_frm.cscript.primary_process_costing=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	if (d.primary_process_costing){
	return $c_obj(doc, 'get_pp_total_price', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
	}
}
//anand
cur_frm.cscript.sub_machining_costing=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	if (d.sub_machining_costing){
	return $c_obj(doc, 'get_sm_total_price', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
	}
}
//anand
cur_frm.cscript.secondary_process_costing=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	if (d.secondary_process_costing){
	return $c_obj(doc, 'get_sp_total_price', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
	}
}
cur_frm.cscript.r_qty1=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	return $c_obj(doc, 'set_rate', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
}
cur_frm.cscript.r_qty2=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	return $c_obj(doc, 'set_rate', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
}
cur_frm.cscript.r_qty3=function(doc,cdt,cdn){
	var d = locals[cdt][cdn]
	return $c_obj(doc, 'set_rate', d.idx, function(r, rt) {
			refresh_field('multiple_quantity_item');
		});
}

cur_frm.cscript.rfq_material = function() {
	return frappe.call({
			doc: cur_frm.doc,
			method: "get_rfq",
			args:{
				field_name:"raw_material_costing",
				clild_doc_type:"Raw Material Costing Details",
				parent_cost:"Raw Material Cost Sheet",
				child_docname:"raw_material_costing_details",
				rfq_doctype:"Material RFQ",
				rfq_child:"material_rfq_details"

			},
			callback: function(r) {
				if(r.exc) {
					msgprint(__("There were errors."));
					return;
				}
				else if (r.message){
					msgprint(__("{0} RFQ's Updated.",[r.message]));
				}
				cur_frm.refresh();
			}
		});
}

cur_frm.cscript.rfq_pp = function() {
	return frappe.call({
			doc: cur_frm.doc,
			method: "get_rfq",
			args:{
				field_name:"primary_process_costing",
				clild_doc_type:"Primary Process Details",
				parent_cost:"Primary Process Costing",
				child_docname:"primary_process",
				rfq_doctype:"Primary Process RFQ",
				rfq_child:"primary_process_rfq_details"

			},
			callback: function(r) {
				if(r.exc) {
					msgprint(__("There were errors."));
					return;
				}
				else if (r.message){
					msgprint(__("{0} RFQ's Updated.",[r.message]));
				}
				cur_frm.refresh();
			}
		});
	
}

cur_frm.cscript.rfq_sp = function() {
	return frappe.call({
			doc: cur_frm.doc,
			method: "get_rfq",
			args:{
				field_name:"secondary_process_costing",
				clild_doc_type:"Secondary Process Details",
				parent_cost:"Secondary Process Costing",
				child_docname:"secondary_process",
				rfq_doctype:"Secondary Process RFQ",
				rfq_child:"secondary_process_rfq_details"

			},
			callback: function(r) {
				if(r.exc) {
					msgprint(__("There were errors."));
					return;
				}
				else if (r.message){
					msgprint(__("{0} RFQ's Updated.",[r.message]));
				}
				cur_frm.refresh();
			}
		});
	
}

cur_frm.cscript.rfq_sm = function() {
	return frappe.call({
			doc: cur_frm.doc,
			method: "get_rfq",
			args:{
				field_name:"sub_machining_costing",
				clild_doc_type:"Sub Machining Details",
				parent_cost:"Sub Machining Costing",
				child_docname:"sub_machining",
				rfq_doctype:"Sub Machining RFQ",
				rfq_child:"sub_machining_rfq_details"

			},
			callback: function(r) {
				if(r.exc) {
					msgprint(__("There were errors."));
					return;
				}
				else if (r.message){
					msgprint(__("{0} RFQ's Updated.",[r.message]));
				}
				cur_frm.refresh();
			}
		});
}
