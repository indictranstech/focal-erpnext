cur_frm.cscript.mark_percent=function(doc,cdt,cdn){
	var d = frappe.get_doc(cdt, cdn);
	rate=d.exchange_rate*(d.unit_cost+(d.unit_cost*d.mark_percent/100))
	d.price_with_markup=rate
   	return $c_obj(doc, 'set_sp_total', d.idx, function(r, rt) {
			refresh_field("secondary_process")
			refresh_field("sp_total")
		});
}
cur_frm.cscript.new_rfq=function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	return $c_obj(doc, 'create_new_rfq', d.idx, function(r, rt) {
			refresh_field("secondary_process")
			refresh_field("quote_ref")
	});
}

cur_frm.cscript.current_rfq=function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	return $c_obj(doc, 'update_new_rfq', d.idx, function(r, rt) {
			refresh_field("secondary_process")
			refresh_field("quote_ref")
	});
}