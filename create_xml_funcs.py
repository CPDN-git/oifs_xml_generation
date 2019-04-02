#! /usr/bin/env python

# Program : create_xml_funcs.py
# Author  : Sarah Sparrow modified from CPDN script.
# Purpose : functions for creating the openifs xml.

from xml.etree.ElementTree import *
from ANC import *

def get_upload_info(upload_loc):
        # Dictionary of upload file handlers
        upload_info_dict={"alpha":("alpha","http://alpha.cpdn.org/cgi-bin/file_upload_handler"),\
		"dev":("dev","https://dev.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload2":("upload2","http://upload2.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload3":("upload3","http://upload3.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload4":("upload4","http://upload4.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload5":("upload5","http://upload5.cpdn.org/cpdn_cgi_main/file_upload_handler"),\
                "upload6":("upload6","http://upload6.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload7":("upload7","http://upload7.cpdn.org/cgi-bin/file_upload_handler"),\
                "upload8":("upload8","http://upload8.cpdn.org/cgi-bin/file_upload_handler"),
                "upload9":("upload9","http://upload9.cpdn.org/cgi-bin/file_upload_handler"),
                "upload10":("upload10","http://upload10.cpdn.org/cgi-bin/file_upload_handler"),
                "upload11":("upload11","http://upload11.cpdn.org/cgi-bin/file_upload_handler"),
                "upload12":("upload12","http://upload12.cpdn.org/cgi-bin/file_upload_handler")}

        upload_handler=upload_info_dict[upload_loc][1]
        upload_template="upload_templates/"+upload_info_dict[upload_loc][0]+"/result_template_"+upload_loc

        return upload_handler,upload_template

# Take dictionary of parameters and add experiment to the xml
def CreateWorkunit(params, ic_ancil,ifs_data,climate_data):
	# Set experiment and parameters tags and add to document
	Workunit=Element('workunit')
        WU_tree=ElementTree(Workunit)	

	# Loop over parameters and add
	for param,value in sorted(params.iteritems()):
		SubElement(Workunit, param).text=str(value)

	
	# Add initial data file
        ica=Element('ic_ancil')
        ica_tree=ElementTree(ica)
	for param,value in sorted(ic_ancil.iteritems()):
                SubElement(ica, param).text=str(value)	
	
	# Add ifs_data files
	ifsd=Element('ifsdata')
        ifsd_tree=ElementTree(ifsd)
	for param,value in sorted(ifs_data.iteritems()):
        	SubElement(ifsd, param).text=str(value)

	# Add climate_data files
        clid=Element('climate_data')
        clid_tree=ElementTree(clid)
        for param,value in sorted(climate_data.iteritems()):
                SubElement(clid, param).text=str(value)

	Workunit.append(ica)
	Workunit.append(ifsd)
	Workunit.append(clid)
	return Workunit
 
	


# Adds batch tags to xml file
def AddBatchInfo(batch):
	# Add batch information files
        binf=Element('batch_info')
        binf_tree=ElementTree(binf)
        for param,value in sorted(batch.iteritems()):
                SubElement(binf, param).text=str(value)

	SubElement(binf, 'workunit_range').text="workunit_range"
	SubElement(binf, 'batchid').text="batchid"
	return binf
