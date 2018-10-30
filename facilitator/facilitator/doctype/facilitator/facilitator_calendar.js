frappe.views.calendar["Facilitator"] = {
	field_map:{
		"start": "start_on",
		"end": "end_on",
		"id": "name",
		"allDay":false,
		"title": "title",
		"doctype":"doctype",
		"color":"color"
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "facilitator",
			"options": "Facilitator",
			"label": __("Facilitator")
		}
	],

	get_events_method: "erpnext.buying.doctype.purchase_order.purchase_order.getData"

}

