#!/usr/bin/env python

import csv
import os
import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom

from dashboard_generate import *

from splunklib.searchcommands import dispatch, \
                                     GeneratingCommand, \
                                     Configuration, \
                                     Option, \
                                     validators
from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

################################################################################
@Configuration()
class GenerateDashboards(GeneratingCommand):
    #contants
    BASE_DIR = make_splunkhome_path(["etc","apps","search_catalog"])
    DASHBOARD_PATH = os.path.join(BASE_DIR,'local','data','ui','views')
    NAV_FILE = os.path.join(BASE_DIR,'local','data','ui','nav','default.xml')
    LOOKUP_FILE = os.path.join(BASE_DIR,'lookups','search_catalog.csv')

    testmode = Option(
        doc='''**Syntax:** **testmode=***<boolean>*
        **Description:** Used to stop the command from running on dashboards''',
        ) 	

    def generate(self):

        if self.testmode:
            if re.search(r'(?i)^t(?:rue)?', self.testmode):
                testmode = True
        else:
            testmode = False
        if testmode:
            text = 'Test Mode'
            yield {'_raw': text}
            sys.exit()
        
        #make directories if they don't exist
        nav_dir = os.path.dirname(self.NAV_FILE)
        if not os.path.exists(nav_dir):
            os.makedirs(nav_dir)
        views_dir = self.DASHBOARD_PATH
        if not os.path.exists(views_dir):
            os.makedirs(views_dir)

        #remove old dashboards
        file_list = os.listdir(self.DASHBOARD_PATH)
        for f in file_list:
            if not f.startswith('_'):
                file_path = self.DASHBOARD_PATH + os.sep + f
                os.remove(file_path)


        #setup standard menu items
        root = ET.Element("nav", color="#0ED3A6", search_view="search")
        default = ET.SubElement(root, "view", default="true", name="_welcome")
        catalog = ET.SubElement(root, "collection", label="Search Catalog")
        #search = ET.SubElement(root, "view", name="search")
        search = ET.SubElement(root, "collection", label="Search")
        config = ET.SubElement(root, "collection", label="Config")
        #So far unable to get the SA-Utils integration working
        #disabling this option for now
        #ET.SubElement(config, "view", name="_edit")
        ET.SubElement(config, "a", 
            href="/app/lookup_editor/lookup_edit?owner=nobody&namespace=search_catalog&lookup=search_catalog.csv&type=csv"). \
            text = "Edit CSV (Requires Lookup Editor App)"
        ET.SubElement(config, "view", name="_add_search")
        ET.SubElement(config, "view", name="_refresh")
        ET.SubElement(search, "view", name="_search")
        ET.SubElement(search, "view", name="_latest")
        ET.SubElement(search, "view", name="search")
        
        #iterate over CSV and create sub menus
        input_file = csv.DictReader(open(self.LOOKUP_FILE))
        collection_dict = {}
        n = 0
        for row in input_file:
            if row['type']:
                if row['type'] == 'section':
                    collection_dict[row['name']] = ET.SubElement(
                        catalog, 
                        "collection", 
                        label=row['name']
                        )
                if row['type'] == 'subsection':
                    subsection_name = row['name'] + row['parent']
                    collection_dict[subsection_name] = ET.SubElement(
                        collection_dict[row['parent']], 
                        "collection", 
                        label=row['name']
                        )
            else:
                xname = re.sub('[ \.]', '_', row['name'].lower())
                if row['parent'] == row['section']:
                    parent_name = row['parent']
                else:
                    parent_name = row['parent'] + row['section']
                ET.SubElement(collection_dict[parent_name], "view", name=xname)
        	filename = os.path.join(self.DASHBOARD_PATH, xname)
                if row['notes']:
        	    dashboard_generate(
                        row['name'],
                        row['search'], 
                        row['display'], 
                        filename, 
                        dashboard_notes=row['notes']
                        )
                else:
        	    dashboard_generate(
                        row['name'], 
                        row['search'], 
                        row['display'], 
                        filename
                        )
                n += 1

        #write menu to nav file
        xml_string = ET.tostring(root)
        xml_output = xml.dom.minidom.parseString(xml_string)
        pretty_xml_as_string = xml_output.toprettyxml(indent="  ")
        f = open(self.NAV_FILE, 'w')
        f.write(pretty_xml_as_string)
        f.close

        #Display output of results to Splunk
        text = '%d Dasbhoards Generated' % n
        yield {'result': text}


dispatch(GenerateDashboards, sys.argv, sys.stdin, sys.stdout, __name__)
