import csv
import re
import urllib
import xml.etree.cElementTree as ET
import xml.dom.minidom

def dashboard_generate(label, main_search, display, filename=False, dashboard_notes=False): 
    pretty = DashboardGenerate('form', label)
    pretty.add_base_search(search='|fieldsummary |table field distinct_count values', search_id='sub_search', base_search='base_search')
    pretty.add_row(3)
    if dashboard_notes:
        pretty.add_notes_panel(2,main_search, notes=dashboard_notes)
    else:
        pretty.add_notes_panel(2,main_search)
    pretty.add_chart_panel(3, '| search NOT [| inputlookup most_populated_filter | format ] | sort -distinct_count | head 5 | table field distinct_count', title='Most Populated Fields', base_search='sub_search', height='137')
    table_color_dict = {
        'count': 
	    { 'colorPalette':
	        { 'type': 'minMidMax', 'maxColor': '#0E3BD3', 'midColor': '#FFFFFF', 'minColor': '#C3CEF4' },
	      'scale':
                { 'type': 'minMidMax', 'midType': 'percent', 'midValue': '50', 'minType': 'percent', 'minValue': '10' }	    
	    },
        'default field':
	    { 'colorPalette':
                { 'type': 'map', '_text': '{"host":#E1FAF4,"source":#C3F4E9,"sourcetype":#A5EFDE,"index":#87E9D2}' },
            }
    }
    if display == 'table':
        field_summary_search = r'stats count'
	pretty.add_single_value_panel(3, field_summary_search, title='Number of fields/columns', base_search='sub_search', bgcolor='C3CEF4')
        pretty.add_table_panel(4, main_search, title='Results', search_id='base_search', time_picker=True, row_count='20')
    else:	    
        field_summary_search = r'| search field IN (host source sourcetype index) |table field distinct_count values |rename field AS "default field" distinct_count AS count |eval values = replace(values, "{\"value\":\"([^\"]+)\",\"count\":\d+}", "\1"), values=replace(values, "\[|\]", "")'
        pretty.add_table_panel(3, field_summary_search, title='Default Field Values', base_search='sub_search', color_dict=table_color_dict)
        pretty.add_events_panel(4, main_search, title='Events', search_id='base_search', time_picker=True)
    if filename:
        pretty.pretty_xml(filename)
    else:
        return pretty.pretty_xml()

class DashboardGenerate(object):
    
    def __init__(self, dashboard_type, label):
        if dashboard_type=='form':
            self.root = ET.Element('form', stylesheet='search_catalog.css', hideEdit='true')
	else:
            self.root = ET.Element('dashboard')
        label = ET.SubElement(self.root, 'label').text = label

    def add_row(self, num):
        """
	Add row(s) to the dashboard. Provide a number for the quantity of rows added.
	"""
        i = 0
        while i < num: 
            ET.SubElement(self.root, 'row')
	    i += 1
    
    def add_base_search(self, search, search_id, base_search=False, earliest=False, latest=False):
	if not base_search:
            search_root = ET.SubElement(self.root, 'search', id=search_id)
	    ET.SubElement(search_root, 'query').text = search
	    ET.SubElement(search_root, 'earliest', id=search_id).text = earliest
	    ET.SubElement(search_root, 'latest', id=search_id).text = latest
	else:
            search_root = ET.SubElement(self.root, 'search', id=search_id, base=base_search)
	    ET.SubElement(search_root, 'query').text = search

    def add_notes_panel(self, row_num, search, notes=False):
        """
	Generate a panel with no borders showing the search to be run along with notes.
	"""
        panel = ET.SubElement(self.root[row_num], 'panel')
	panelhtml = ET.SubElement(panel, 'html')
        panelhtmldiv = ET.SubElement(panelhtml, 'div', {'class':'hidden_panel'})
        if notes:
	    ET.SubElement(panelhtmldiv, 'h4').text = 'Notes'
	    ET.SubElement(panelhtmldiv, 'p').text = notes
	ET.SubElement(panelhtmldiv, 'h4').text = 'Search'
	ET.SubElement(panelhtmldiv, 'pre').text = search
	ET.SubElement(panelhtmldiv, 'a', target='_blank', href='/app/search/search?q='+urllib.quote_plus(search)+'&amp;display.page.search.tab=events&amp;display.general.type=events&amp;earliest=$time.earliest$&amp;latest=$time.latest$').text = 'Click to open in search'

    def add_chart_panel(self, row_num, search, chart_type=False, title=False, base_search=False, earliest=False, latest=False, height=False):
        """
	Generate a chart panel. Provide the row_number and search. Defaults to bar chart.
	"""
        panel = ET.SubElement(self.root[row_num], 'panel')
	if title:
	    ET.SubElement(panel, 'title').text = title
	panelchart = ET.SubElement(panel, 'chart')
        if base_search:
	    panelchartsearch = ET.SubElement(panelchart, 'search', base=base_search)
	    ET.SubElement(panelchartsearch, 'query').text = search
	else:
	    panelchartsearch = ET.SubElement(panelchart, 'search')
	    ET.SubElement(panelchartsearch, 'query').text = search
	    ET.SubElement(panelchartsearch, 'earliest', id=search_id).text = earliest
	    ET.SubElement(panelchartsearch, 'latest', id=search_id).text = latest
	ET.SubElement(panelchart, 'option', name='charting.axisTitleX.visibility').text = 'collapsed'
	ET.SubElement(panelchart, 'option', name='charting.axisTitleY.visibility').text = 'collapsed'
	if chart_type:
	    ET.SubElement(panelchart, 'option', name='charting.chart').text = chart_type
	else:
	    ET.SubElement(panelchart, 'option', name='charting.chart').text = 'bar'
	ET.SubElement(panelchart, 'option', name='charting.drilldown').text = 'none'
	ET.SubElement(panelchart, 'option', name='charting.legend.placement').text = 'none'
	if height:
            ET.SubElement(panelchart, 'option', name='height').text = height

    def add_single_value_panel(self, row_num, search, chart_type=False, title=False, base_search=False, earliest=False, latest=False, height=False, bgcolor=False):
        """
	Generate a single value panel. 
	"""
        panel = ET.SubElement(self.root[row_num], 'panel')
	if title:
	    ET.SubElement(panel, 'title').text = title
	panelsingle = ET.SubElement(panel, 'single')
        if base_search:
	    panelsinglesearch = ET.SubElement(panelsingle, 'search', base=base_search)
	    ET.SubElement(panelsinglesearch, 'query').text = search
	else:
	    panelsinglesearch = ET.SubElement(panelsingle, 'search')
	    ET.SubElement(panelsinglesearch, 'query').text = search
	    ET.SubElement(panelsinglesearch, 'earliest', id=search_id).text = earliest
	    ET.SubElement(panelsinglesearch, 'latest', id=search_id).text = latest
	ET.SubElement(panelsingle, 'option', name='drilldown').text = 'none'
	if bgcolor:
	    ET.SubElement(panelsingle, 'option', name='colorMode').text = 'block'
	    ET.SubElement(panelsingle, 'option', name='useColors').text = '1'
	    ET.SubElement(panelsingle, 'option', name='rangeColors').text = '["0x'+bgcolor+'","0x'+bgcolor+'"]'
	    ET.SubElement(panelsingle, 'option', name='rangeValues').text = '[0]'

    def add_table_panel(self, row_num, search, title=False, search_id=False, base_search=False, earliest=False, latest=False, height=False, color_dict=False, time_picker=False, row_count=False):
        """
	Generate a table panel. Provide the row_number and search.
	"""
        panel = ET.SubElement(self.root[row_num], 'panel')
	if title:
	    ET.SubElement(panel, 'title').text = title
	if time_picker:
	    panelinput = ET.SubElement(panel, 'input', type='time', token='time', searchWhenChanged='true')
	    panelinputdefault = ET.SubElement(panelinput, 'default')
	    if not earliest:
	        earliest = '-24h@h'
	    if not latest:
	        latest = 'now'
	    ET.SubElement(panelinputdefault, 'earliest').text = earliest
	    ET.SubElement(panelinputdefault, 'latest').text = latest
	paneltable = ET.SubElement(panel, 'table')
        if search_id:
            if base_search:
	        paneltablesearch = ET.SubElement(paneltable, 'search', base=base_search, id=search_id)
	        ET.SubElement(paneltablesearch, 'query').text = search
	    else:
	        paneltablesearch = ET.SubElement(paneltable, 'search', id=search_id)
	        ET.SubElement(paneltablesearch, 'query').text = search
	        if time_picker:
	            ET.SubElement(paneltablesearch, 'earliest').text = '$time.earliest$'
	            ET.SubElement(paneltablesearch, 'latest').text = '$time.latest$'
                else:
	            ET.SubElement(paneltablesearch, 'earliest').text = earliest
	            ET.SubElement(paneltablesearch, 'latest').text = latest
	else:
            if base_search:
	        paneltablesearch = ET.SubElement(paneltable, 'search', base=base_search)
	        ET.SubElement(paneltablesearch, 'query').text = search
	    else:
	        paneltablesearch = ET.SubElement(paneltable, 'search')
	        ET.SubElement(paneltablesearch, 'query').text = search
	        if time_picker:
	            ET.SubElement(paneltablesearch, 'earliest').text = '$time.earliest$'
	            ET.SubElement(paneltablesearch, 'latest').text = '$time.latest$'
                else:
	            ET.SubElement(paneltablesearch, 'earliest').text = earliest
	            ET.SubElement(paneltablesearch, 'latest').text = latest
	if row_count:
	    ET.SubElement(paneltable, 'option', name='count').text = row_count
	ET.SubElement(paneltable, 'option', name='dataOverlayMode').text = 'none'
	ET.SubElement(paneltable, 'option', name='drilldown').text = 'none'
	ET.SubElement(paneltable, 'option', name='rowNumbers').text = 'false'
	ET.SubElement(paneltable, 'option', name='wrap').text = 'false'
	if color_dict and isinstance(color_dict, dict):
	    for color_field, value in color_dict.items():
		paneltableformat = ET.SubElement(paneltable, 'format', field=color_field, type='color')
		if value['colorPalette']['type'] == 'minMidMax':
		    paneltableformatcp = ET.SubElement(paneltableformat, 'colorPalette')
		    for k,v in value['colorPalette'].items():
		        paneltableformatcp.set(k, v)
		    paneltableformatscale = ET.SubElement(paneltableformat, 'scale')
		    for k,v in value['scale'].items():
		        paneltableformatscale.set(k, v)
		if value['colorPalette']['type'] == 'map':
		    ET.SubElement(paneltableformat, 'colorPalette', type='map').text = value['colorPalette']['_text']

    def add_events_panel(self, row_num, search, title=False, search_id=False, base_search=False, earliest=False, latest=False, height=False, time_picker=False):
        """
	Generate events panel. Provide the row_number and search.
	"""
        panel = ET.SubElement(self.root[row_num], 'panel')
	if title:
	    ET.SubElement(panel, 'title').text = title
	if time_picker:
	    panelinput = ET.SubElement(panel, 'input', type='time', token='time', searchWhenChanged='true')
	    panelinputdefault = ET.SubElement(panelinput, 'default')
	    if not earliest:
	        earliest = '-24h@h'
	    if not latest:
	        latest = 'now'
	    ET.SubElement(panelinputdefault, 'earliest').text = earliest
	    ET.SubElement(panelinputdefault, 'latest').text = latest
	panelevent = ET.SubElement(panel, 'event')
	if search_id:
	    search += '|table *'
	    paneleventsearch = ET.SubElement(panelevent, 'search', id=search_id)
	    ET.SubElement(paneleventsearch, 'query').text = search
	    if time_picker:
	        ET.SubElement(paneleventsearch, 'earliest').text = '$time.earliest$'
	        ET.SubElement(paneleventsearch, 'latest').text = '$time.latest$'
            else:
	        ET.SubElement(paneleventsearch, 'earliest').text = earliest
	        ET.SubElement(paneleventsearch, 'latest').text = latest
        else:
	    paneleventsearch = ET.SubElement(panelevent, 'search')
	    ET.SubElement(paneleventsearch, 'query').text = search
	    ET.SubElement(paneleventsearch, 'earliest').text = earliest
	    ET.SubElement(paneleventsearch, 'latest').text = latest
	ET.SubElement(panelevent, 'option', name='count').text = '20'
	ET.SubElement(panelevent, 'option', name='list.drilldown').text = 'none'
	ET.SubElement(panelevent, 'option', name='list.wrap').text = '1'
	ET.SubElement(panelevent, 'option', name='maxLines').text = '5'
	ET.SubElement(panelevent, 'option', name='raw.drilldown').text = 'none'
	ET.SubElement(panelevent, 'option', name='rowNumbers').text = '0'
	ET.SubElement(panelevent, 'option', name='table.drilldown').text = 'none'
	ET.SubElement(panelevent, 'option', name='table.sortDirection').text = 'asc'
	ET.SubElement(panelevent, 'option', name='table.wrap').text = '1'
	ET.SubElement(panelevent, 'option', name='type').text = 'list'

    def pretty_xml(self, filename=False):
        """
	Format the XML output to be indented.
	"""
        xml_string = ET.tostring(self.root)
        xml_dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml_as_string = xml_dom.toprettyxml(indent='  ')
	if filename:
            filename = filename + '.xml'
            f = open(filename, 'w')
	    f.write(pretty_xml_as_string)
	    f.close
        else:
	    return pretty_xml_as_string
