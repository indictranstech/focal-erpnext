
cur_frm.cscript.inspected_by=function(doc,cdt,cdn){
	return frappe.call({
		doc:cur_frm.doc,
		method: "get_concat_det",
		callback:function(r){
			refresh_field('inspector_name')

		}
	})
}


cur_frm.cscript.onload=function(doc){
	if (doc.quantity){
		q=(parseInt(doc.quantity)/5)
		doc.r_qty=Math.ceil(q)
	}
}

cur_frm.cscript.job_no=function(doc){
	return frappe.call({
			doc: cur_frm.doc,
			method: "get_details",
			callback: function(r) {
				if (doc.quantity){
		            q=(parseInt(doc.quantity)/5)
		            doc.r_qty=Math.ceil(q)
		        }
				refresh_field(['customer_code','part_name','part_no','drawing_no','quantity','po_no','batch_no']);
			}
		});
}

/*cur_frm.cscript.validate=function(doc){
	
}
*/
cur_frm.cscript.measurements=function(doc,cdt,cdn){
	d=locals[cdt][cdn]
	if (d.actual_mesurement){
		am = locals['Actual Mesurement'][d.actual_mesurement];
		am.from_doc=doc.name
		loaddoc('Actual Mesurement', d.actual_mesurement);
	}
	else{
		var am = frappe.model.make_new_doc_and_get_name('Actual Mesurement');
		am = locals['Actual Mesurement'][am];
		am.from_doc=doc.name
		am.idx=d.idx
		for(i=0;i<doc.quantity;i++){
			var d1 = frappe.model.add_child(am, 'Mesurement Values', 'mesurement_values');
		}
		loaddoc('Actual Mesurement', am.name);
	}	
}

cur_frm.cscript.quantity=function(doc,cdt,cdn){
	if (doc.quantity){
		q=(parseInt(doc.quantity)/5)
		doc.r_qty=Math.ceil(q)
	}

}
 