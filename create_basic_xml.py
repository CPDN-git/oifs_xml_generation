#! /usr/bin/env python

# Program : create_basic_xml.py
# Author  : Sarah Sparrow (modified from the CPDN script)
# Purpose : create openIFS experiment xmls

import os,sys
#from xml.etree.ElementTree import *
import xml.etree.ElementTree as ET
from ANC import *
from xml.dom import minidom

from create_xml_funcs import *

def create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens,upload_loc,start_umid, model_class,model_config, fullpos_namelist):
	print "Creating experiments... "
	ic_ancil={}
	# Start the xml document
  	outtreeroot=Element('batch')
  	outtree=ElementTree(outtreeroot)

	# Add in the model config
	SubElement(outtreeroot, 'model_class').text=str(model_class)
        SubElement(outtreeroot, 'model_config').text=str(model_config)
	SubElement(outtreeroot, 'fullpos_namelist').text=str(fullpos_namelist)

	# Add in the upload information
	upload_handler,upload_template=get_upload_info(upload_loc)
        ul_info=Element('upload_info')
	ul_tree=ElementTree(ul_info)
	SubElement(ul_info, 'upload_handler').text=str(upload_handler)
	SubElement(ul_info, 'result_template_prefix').text=str(upload_template)	
	outtreeroot.append(ul_info)
	
	# Create the workunits section
	WUs=Element('workunits')
        WUs_tree=ElementTree(WUs)

	# Setup the umid counter
	anc = ANC()
        anc.Start(start_umid) # next set

	count=0
	for date in dates:
        	params['start_year']=date[0:4]
                params['start_month']=date[4:6]
                params['start_day']=date[6:8]
                params['start_hour']=date[-2:]

                for ia in range(0,n_analysis):
                        ic_ancil['ic_ancil_zip']='ic_'+params['exptid']+'_'+date+'_'+str(ia).zfill(2)+'.zip'                  
                        params['analysis_member_number']=str(ia).zfill(2)
			for iens in range(0,n_ens):  
                                params['ensemble_member_number']=str(iens).zfill(2)
				params['unique_member_id']=anc.Get()

                                wu=CreateWorkunit(params,ic_ancil,ifs_data,climate_data)
				WUs.append(wu)
				anc.Next()
				count +=1
	# Add the workunits to the xml
	outtreeroot.append(WUs)
       	
	end_umid=params['unique_member_id'] 

        # Add in start and end umid to batch tags:
        batch['umid_start']=start_umid
        batch['umid_end']=end_umid
        binf=AddBatchInfo(batch)
        outtreeroot.append(binf)

        ######## Write out the file ########
	#Write overall tree stucture to output xml


        xml_out='wu_oifs_'+batch['name'].replace(" ","")+"_" +\
                          start_umid + '_' + end_umid + '.xml'
        if not os.path.exists('xmls'):
                    os.makedirs('xmls')
        print 'Writing to:',xml_out,'...'
        #outtree.write('xmls/'+xml_out)

	xmlstr = minidom.parseString(ET.tostring(outtreeroot)).toprettyxml(indent="   ")
	with open("xmls/"+xml_out, "w") as f:
    		f.write(xmlstr)
        # Print out the number of xmls
        print "Number of workunits: ",count


def main():
	# Declare dictionaries
	params={}
	ifs_data={}
        climate_data={}
        ic_ancil={}
	batch={}

	# Define date ranges in the file
	dates=['2000010100','2001010206']

	# Define number of analysis numbers
	n_analysis=2

	# Define number of ensemble members
	n_ens=2

	# Set up doc
        upload_loc="upload3"
        
	# Set start umid		
	start_umid = "b000"

	# Set the model configuration
	model_class='openifs'
	model_config='40r1_T159.xml'
	fullpos_namelist='test_fullpos.gz'

	# Parameters for simulations
        params['exptid']='gw3a'
        params['fclen']=1
        params['fclen_units']='days'


	# Climate data and ifs data
	ifs_data['SO4_zip']='SO4.zip'
	ifs_data['radiation_zip']='radiation.zip'
	ifs_data['CFC_zip']='CFC.zip'
	climate_data['climate_data_zip']='climate_data.zip'

	# Add in batch tags:
        batch['name']="Storm Desmond"
        batch['desc']="Storm Desmond case study analysis"
        batch['owner']="Glenn Carver <Glenn.Carver@ecmwf.int>, Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
        batch['tech_info']="Initialised with ERA5 data with 40 initial conditions"
        batch['proj']='TESTING'

	create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens, upload_loc, start_umid, model_class, model_config,fullpos_namelist)

	print 'Done!'

if __name__ == "__main__":
	main()
