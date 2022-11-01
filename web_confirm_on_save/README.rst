=========================
Web Dialog Confirm on Save
=========================

Show dialog to confirm or alert on form view after save a record:

- Add confirm="message" to show confirm, user can decide continue or cancel

- Add alert="message" to show alert after record has been saved

Example: <form string="Product" confirm="Are you sure to save this product?">


If you want to check condition to show dialog, add this function to model:
```python
    @api.model
    def check_condition_show_dialog(self, record_id, data_changed):
	""" 
	    :param:   self: current model
	              record_id: id of record if save on write function, False on create function
	              data_changed: data changed on form
	    :returns: True: show dialog
	              False: ignore dialog
	"""
	return True
```

Return False to ignore show dialog after custom check
