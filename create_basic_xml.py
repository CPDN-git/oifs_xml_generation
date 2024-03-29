#! /usr/bin/env python

# Program : create_basic_xml.py
# Author  : Sarah Sparrow (modified from the CPDN script)
# Purpose : create openIFS experiment xmls

import os,sys,time
#from xml.etree.ElementTree import *
import xml.etree.ElementTree as ET
from ANC import *
from xml.dom import minidom
from ast import literal_eval

from create_xml_funcs import *


host='pandia'

if host=='caerus' or host =='hesperus':
	proj_dir='/storage/www/cpdnboinc/'
elif host=='pandia':
	proj_dir='/storage/www/cpdnboinc_dev/'

def create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens,s_ens,upload_loc,start_umid, model_class,model_config, fullpos_namelist, num_threads):
    print "Creating experiments... "
    ic_ancil={}
    # Start the xml document
    outtreeroot=Element('batch')
    outtree=ElementTree(outtreeroot)

    # Add in the model config
    SubElement(outtreeroot, 'model_class').text=str(model_class)
    SubElement(outtreeroot, 'model_config').text=str(model_config)
    SubElement(outtreeroot, 'fullpos_namelist').text=str(fullpos_namelist)
    SubElement(outtreeroot, 'num_threads').text=str(num_threads)

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
            ic_ancil['ic_ancil_zip']='ic_'+params['exptid']+'_'+date+'_'+str(ia).zfill(3)+'.zip'                  
            params['analysis_member_number']=str(ia).zfill(3)
            for iens in range(s_ens,s_ens+n_ens):  
                params['ensemble_member_number']=str(iens).zfill(3)
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

    timestr = time.strftime("%Y%m%d-%H%M%S")
    xml_out='wu_oifs_'+batch['name'].replace(" ","")+"_" +start_umid + '_' + end_umid + '_'+timestr+'.xml'
    if not os.path.exists(proj_dir+'/oifs_workgen/xml_staging'):
        os.makedirs(proj_dir+'/oifs_workgen/xml_staging')
    print 'Writing to:',xml_out,'...'
    #outtree.write('xmls/'+xml_out)

    xmlstr = minidom.parseString(ET.tostring(outtreeroot)).toprettyxml(indent="   ")
    with open(proj_dir+"/oifs_workgen/xml_staging/"+xml_out, "w") as f:
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
    s_ens=0

    # Set up doc
    upload_loc="upload11"
        
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
    ifs_data['other_radiation_zip']='other_radiation.zip'
    ifs_data['GHG_zip']='GHG.zip'
    climate_data['climate_data_zip']='climate_data.zip'

    # Add in batch tags:
    batch['name']="Storm Desmond"
    batch['desc']="Storm Desmond case study analysis"
    batch['owner']="Glenn Carver <Glenn.Carver@ecmwf.int>, Sarah Sparrow <sarah.sparrow@oerc.ox.ac.uk>"
    batch['tech_info']="Initialised with ERA5 data with 40 initial conditions"
    batch['proj']='TESTING'

    num_threads=1

    create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens,s_ens, upload_loc, start_umid, model_class, model_config,fullpos_namelist,num_threads)
    CreateFort4(params,dates,s_ens,start_umid,model_config,fullpos_namelist)

    print 'Done!'

if __name__ == "__main__":
    main()
