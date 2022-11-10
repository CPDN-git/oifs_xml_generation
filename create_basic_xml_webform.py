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

from socket import gethostname


host=gethostname()
if host=='caerus' or host =='hesperus':
	proj_dir='/storage/www/cpdnboinc/'
elif host=='pandia':
	proj_dir='/storage/www/cpdnboinc_dev/'

def create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens,s_ens,upload_loc,start_umid,
               model_class,model_config, fullpos_namelist,num_threads,variable_vectors):
    print("Creating experiments... ")
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
    print('Writing to:'+xml_out+'...')
    #outtree.write('xmls/'+xml_out)

    xmlstr = minidom.parseString(ET.tostring(outtreeroot)).toprettyxml(indent="   ")
    with open(proj_dir+"/oifs_workgen/xml_staging/"+xml_out, "w") as f:
            f.write(xmlstr)
    # Print out the number of xmls
    print("Number of workunits: "+count)


def main():
    data=sys.argv[1]
    
    fdata=data.replace('\\','') 
    form_data=literal_eval(fdata)
    
    # Declare dictionaries
    params={}
    ifs_data={}
    climate_data={}
    ic_ancil={}
    batch={}

    # Define date ranges in the file
    dates=form_data['start_dates'].split(',')

    # Define number of analysis numbers
    n_analysis=int(form_data['n_analysis'])

    # Define number of ensemble members and starting ensemble member number
    n_ens=int(form_data['n_ens'])
    s_ens=int(form_data['s_ens'])

    # Set up doc
    upload_loc=form_data['upload_loc']
        
    # Set start umid        
    start_umid = form_data['start_umid']
    
    # Set the model configuration
    model_class=form_data['model_class']
    model_config=form_data['model_config']
    fullpos_namelist=form_data['fullpos_namelist']
    
    # Parameters for simulations
    params['exptid']=form_data['exptid']
    params['fclen']=form_data['fclen']
    params['fclen_units']=form_data['fclen_units']

    # Sensitivity experiment
    params['perpara']=form_data['perpara'].split('/')
    params['perboun']=form_data['perboun'].split('/')

    # Climate data and ifs data
    ifs_data['SO4_zip']=form_data['SO4_file']
    ifs_data['other_radiation_zip']=form_data['Rad_file']
    ifs_data['GHG_zip']=form_data['GHG_file']
    climate_data['climate_data_zip']=form_data['climate_data_file']
    
    # Add in batch tags:
    batch['name']=form_data['BatchName']
    batch['desc']=form_data['BatchDesc']
    owner=form_data['BatchOwner']
    owner1=owner.replace('(','<')
    owner2=owner1.replace(')','>')
    batch['owner']=owner2
    batch['tech_info']=form_data['BatchTechInfo']
    batch['proj']=form_data['BatchProj']
    
    num_threads=1

    variable_vectors = CreateSampling(params)
    create_xml(batch,params,ifs_data,climate_data,dates,n_analysis,n_ens,s_ens, upload_loc, start_umid,
               model_class,model_config,fullpos_namelist,num_threads,variable_vectors)
    CreateFort4(params,dates,s_ens,start_umid,model_config,fullpos_namelist,variable_vectors)

    print('Done!')

if __name__ == "__main__":
    main()
