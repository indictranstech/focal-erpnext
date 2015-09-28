cur_frm.cscript.onload=function(doc,cdt,cdn){
	set_label(doc,cdt,cdn);

}

set_label=function(label){
	cur_frm.fields_dict.item_code.set_label('Drawing'+' '+'Code', cur_frm.doc);
	cur_frm.fields_dict.item_name.set_label('Part'+' '+'Name', cur_frm.doc);
    cur_frm.fields_dict.item_group.set_label('Type', cur_frm.doc);
}
cur_frm.cscript.item_name = function(doc) {
	cur_frm.set_value("description", doc.item_name);
}