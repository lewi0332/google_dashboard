import dash_table.FormatTemplate as FormatTemplate

bonus_col = [
    {'name': 'Brand Developer','id': 'brand_developer','selectable': False,'hideable': False},
    {'name': 'Total B.O.B.','id': 'total_bob','selectable': False,'hideable': False, 'type': 'numeric'},
    {'name': 'Total Activations','id': 'activation','selectable': False,'hideable': False, 'type': 'numeric'},
    {'name': 'Total Clinics','id': 'clinics','selectable': False,'hideable': False, 'type': 'numeric'},
    {'name': 'Trail Building Days','id': 'trail_day','selectable': False,'hideable': False, 'type': 'numeric'}
    ]

bonus_cell_cond = [
    {'if': {'column_id':'brand_developer'},'width':60, 'textAlign':'center', 'margin-center':1},
    {'if': {'column_id':'total_bob'},'width':55, 'textAlign':'center'},
    {'if': {'column_id':'activation'},'width':60, 'textAlign':'center'},
    {'if': {'column_id':'clinics'},'width':60, 'textAlign':'center'},
    {'if': {'column_id':'trail_day'},'width':60, 'textAlign':'center'},
    ]

bonus_data_cond = [
    {'if': {'filter_query': "{total_bob} > 150", 'column_id': 'total_bob'},
            'backgroundColor': '#d2f8d2'},
    {'if': {'filter_query': "{activation} > 6", 'column_id': 'total_bob'},
            'backgroundColor': '#d2f8d2'},
    {'if': {'filter_query': "{clinics} > 12", 'column_id': 'total_bob'},
            'backgroundColor': '#d2f8d2'},
    {'if': {'filter_query': "{trail_day} > 1", 'column_id': 'total_bob'},
            'backgroundColor': '#d2f8d2'},
    ]
