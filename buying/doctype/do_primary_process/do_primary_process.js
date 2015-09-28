frappe.provide("erpnext.buying");
{% include 'buying/doctype/purchase_common/purchase_common.js' %};

erpnext.buying.DOPrimaryProcess = frappe.ui.form.Controller.extend({
	refresh: function(doc, cdt, cdn) {
		 
		this.frm.dashboard.reset();
			
	},
});

$.extend(cur_frm.cscript, new erpnext.buying.DOPrimaryProcess({frm: cur_frm}));

cur_frm.fields_dict.po_primary_process.get_query = function(doc) {
	return {filters: { docstatus:1}}
}

cur_frm.cscript.po_primary_process=function(doc,cdt,cdn){
	frappe.model.map_current_doc({
		method: "erpnext.buying.doctype.do_primary_process.do_primary_process.get_po",
		source_name:doc.po_primary_process,
	})
}

