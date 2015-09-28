frappe.provide("erpnext.buying");
{% include 'buying/doctype/purchase_common/purchase_common.js' %};

erpnext.buying.DOMaterial = frappe.ui.form.Controller.extend({
	refresh: function(doc, cdt, cdn) {
		 
		this.frm.dashboard.reset();
			
		
	},
});

$.extend(cur_frm.cscript, new erpnext.buying.DOMaterial({frm: cur_frm}));


cur_frm.fields_dict.po_material_no.get_query = function(doc) {
	return {filters: { docstatus:1}}
}

cur_frm.cscript.po_material_no=function(doc,cdt,cdn){
	frappe.model.map_current_doc({
		method: "erpnext.buying.doctype.do_material.do_material.get_po",
		source_name:doc.po_material_no,
	})
}

