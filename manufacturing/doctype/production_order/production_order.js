// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

$.extend(cur_frm.cscript, {
	onload: function (doc, dt, dn) {

		if (!doc.status) doc.status = 'Draft';
		cfn_set_fields(doc, dt, dn);

		this.frm.add_fetch("sales_order", "delivery_date", "expected_delivery_date");
	},

	before_submit: function() {
		cur_frm.toggle_reqd(["fg_warehouse", "wip_warehouse"], true);
	},

	refresh: function(doc, dt, dn) {
		this.frm.dashboard.reset();
		erpnext.toggle_naming_series();
		this.frm.set_intro("");
		cfn_set_fields(doc, dt, dn);

		if (doc.docstatus === 0 && !doc.__islocal) {
			this.frm.set_intro(__("Submit this Production Order for further processing."));
		} else if (doc.docstatus === 1) {
			var percent = flt(doc.produced_qty) / flt(doc.qty) * 100;
			this.frm.dashboard.add_progress(cint(percent) + "% " + __("Complete"), percent);

			if(doc.status === "Stopped") {
				this.frm.dashboard.set_headline_alert(__("Stopped"), "alert-danger", "icon-stop");
			}
		}
	},

	production_item: function(doc,cdt,cdn) {
		get_server_fields('bom_operations','','',doc,cdt,cdn,1,function(r){refresh_field('bom_operation')})
		return this.frm.call({
			method: "get_item_details",
			args: { item: doc.production_item },
			callback: function(r) {	
				refresh_field('bom_operation')							
			}
		});
	},

	make_se: function(purpose) {
		var me = this;

		frappe.call({
			method:"erpnext.manufacturing.doctype.production_order.production_order.make_stock_entry",
			args: {
				"production_order_id": me.frm.doc.name,
				"purpose": purpose
			},
			callback: function(r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	}
});

var cfn_set_fields = function(doc, dt, dn) {
	if (doc.docstatus == 1) {

		if (doc.status == 'Submitted' || doc.status == 'Material Transferred' || doc.status == 'In Process'){
			cur_frm.add_custom_button(__('Transfer Raw Materials'),
				cur_frm.cscript['Transfer Raw Materials'], frappe.boot.doctype_icons["Stock Entry"]);
			cur_frm.add_custom_button(__('Update Finished Goods'),
				cur_frm.cscript['Update Finished Goods'], frappe.boot.doctype_icons["Stock Entry"]);
		}

		if (doc.status != 'Stopped' && doc.status != 'Completed') {
			cur_frm.add_custom_button(__('Stop'), cur_frm.cscript['Stop Production Order'],
				"icon-exclamation", "btn-default");
		} else if (doc.status == 'Stopped') {
			cur_frm.add_custom_button(__('Unstop'), cur_frm.cscript['Unstop Production Order'],
			"icon-check", "btn-default");
		}
	}
}

cur_frm.cscript['Stop Production Order'] = function() {
	var doc = cur_frm.doc;
	var check = confirm(__("Do you really want to stop production order: " + doc.name));
	if (check) {
		return $c_obj(doc, 'stop_unstop', 'Stopped', function(r, rt) {cur_frm.refresh();});
	}
}

cur_frm.cscript['Unstop Production Order'] = function() {
	var doc = cur_frm.doc;
	var check = confirm(__("Do really want to unstop production order: " + doc.name));
	if (check)
		return $c_obj(doc, 'stop_unstop', 'Unstopped', function(r, rt) {cur_frm.refresh();});
}

cur_frm.cscript['Transfer Raw Materials'] = function() {
	cur_frm.cscript.make_se('Material Transfer');
}

cur_frm.cscript['Update Finished Goods'] = function() {
	cur_frm.cscript.make_se('Manufacture');
}

// cur_frm.fields_dict['production_item'].get_query = function(doc) {
// 	return {
// 		filters:[
// 			['Item', 'is_pro_applicable', '=', 'Yes']
// 		]
// 	}
// }


cur_frm.fields_dict['production_item'].get_query = function(doc) {

	if(doc.sales_order)

		return "select item_code from `tabItem` where is_pro_applicable='Yes' and item_code in (select item_code from `tabSales Order Item` where parent='"+doc.sales_order+"')"

	else
		msgprint("Sales Order field can not be blank")
}

cur_frm.fields_dict['job_order'].get_query = function(doc) {

	if(doc.sales_order)

		return "select name from `tabJob Order` where sales_order='"+doc.sales_order+"' and drawing_no in (select item_code from `tabSales Order Item` where parent='"+doc.sales_order+"')"
		// return "select item_code from `tabItem` where is_pro_applicable='Yes' and item_code in (select item_code from `tabSales Order Item` where parent='"+doc.sales_order+"')"

	else
		msgprint("Sales Order field can not be blank")
}

cur_frm.fields_dict['project_name'].get_query = function(doc, dt, dn) {
	return{
		filters:[
			['Project', 'status', 'not in', 'Completed, Cancelled']
		]
	}
}

cur_frm.set_query("bom_no", function(doc) {
	if (doc.production_item) {
		return{
			query: "erpnext.controllers.queries.bom",
			filters: {item: cstr(doc.production_item)}
		}
	} else msgprint(__("Please enter Production Item first"));
});

cur_frm.add_fetch('bom_no', 'total_fixed_cost', 'total_fixed_cost');



cur_frm.cscript.set_up_time = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}

cur_frm.cscript.time_in_mins = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}

cur_frm.cscript.load_up_time = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}

cur_frm.cscript.tip_change_time = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}

cur_frm.cscript.inspection_time = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}

cur_frm.cscript.hour_rate = function(doc,cdt,cdn) {
	d = locals[cdt][cdn]
	calculate_total_cost(d)
}


function calculate_total_cost (d) {
	sut = 0.0; tim = 0.0; lut = 0.0; tct = 0.0; it = 0.0; hr = 1.0;
	if(d.set_up_time){
	 	sut = d.set_up_time
	 }
	 
	 if(d.time_in_mins){
	 	tim = d.time_in_mins
	 }
	 
	 if(d.load_up_time){
	 	lut= d.load_up_time
	 }

	 if(d.tip_change_time){
	 	tct= d.tip_change_time
	 }

	 if(d.inspection_time){
	 	it= d.inspection_time
	 }

	 if(d.hour_rate){
	 	hr= d.hour_rate
	 }

	d.operating_cost= (parseFloat(sut) + parseFloat(tim) + parseFloat(lut) + parseFloat(tct) + parseFloat(it)) * parseFloat(hr)
	refresh_field("bom_operation")
}
