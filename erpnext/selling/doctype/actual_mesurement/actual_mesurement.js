cur_frm.cscript.onload=function(doc){
	cur_frm.refresh_field("from_doc")	
}
cur_frm.cscript.validate = function(doc) {
	if (doc.__islocal!=1){
		var ci=frappe.model.get_children("Customer Inspection Report",doc.from_doc,"measurements")
		for (i=0;i<ci.length;i++){
			if (doc.idx==ci[i].idx){
				ci[i].actual_mesurement=doc.name
				loaddoc('Customer Inspection Report', doc.from_doc);
			}
		}	
	}	
}
cur_frm.cscript.refresh=function(){
	var obj=frappe.route_options
	if (obj){
		cur_frm.set_value("from_doc",obj.from_doc)
		cur_frm.refresh_field("from_doc")
	}
	frappe.route_options = null;
}

