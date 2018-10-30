frappe.views.calendar["Facilitator Calendar"] = {
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
	eventLimit: true,
 	 views: {
           month: {
             eventLimit: 6 // adjust to 6 only for agendaWeek/agendaDay
             }
         },
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "facilitator",
			"options": "Facilitator",
			"label": __("Facilitator")
		},
		{
			"fieldtype": "Link",
			"fieldname": "event",
			"options": "Event",
			"label": __("Event")
		}
	],

	get_events_method: "facilitator.facilitator.doctype.facilitator_calendar.facilitator_calendar.getData"

}

