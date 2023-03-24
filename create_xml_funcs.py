#! /usr/bin/env python

# Program : create_xml_funcs.py
# Author  : Sarah Sparrow modified from CPDN script.
# Purpose : functions for creating the openifs xml.

import math
from xml.etree.ElementTree import *
from ANC import *
from xml.dom import minidom

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
        upload_template="upload_templates/"+upload_info_dict[upload_loc][0]+"/result_template_oifs"

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

def CreateFort4(params,dates,s_ens,start_umid,model_config,fullpos_namelist):
    # Set some paths to find the config file and 
    project_dir = '/storage/www/cpdnboinc_dev/'
    ifs_ancil_dir = '/storage/cpdn_ancil_files/oifs_ancil_files/'

    date=dates[0]
    params['start_year']=date[0:4]
    params['start_month']=date[4:6]
    params['start_day']=date[6:8]
    params['start_hour']=date[-2:]

    params['analysis_member_number']=str(0).zfill(3)
    params['ensemble_member_number']=str(s_ens).zfill(3)


    # Read information from the configuration file
    xmldoc2 = minidom.parse(project_dir+'oifs_workgen/config_dir/'+model_config)
    
    model_configs = xmldoc2.getElementsByTagName('model_config')
    for model_config in model_configs:
        horiz_resolution = str(model_config.getElementsByTagName('horiz_resolution')[0].childNodes[0].nodeValue)
        vert_resolution = str(model_config.getElementsByTagName('vert_resolution')[0].childNodes[0].nodeValue)
        grid_type = str(model_config.getElementsByTagName('grid_type')[0].childNodes[0].nodeValue)
        timestep = str(model_config.getElementsByTagName('timestep')[0].childNodes[0].nodeValue)
        timestep_units = str(model_config.getElementsByTagName('timestep_units')[0].childNodes[0].nodeValue)
        upload_frequency = str(model_config.getElementsByTagName('upload_frequency')[0].childNodes[0].nodeValue)
        namelist_template = str(model_config.getElementsByTagName('namelist_template_global')[0].childNodes[0].nodeValue)
        wam_namelist_template = str(model_config.getElementsByTagName('wam_template_global')[0].childNodes[0].nodeValue)

	
    # Calculate the number of timesteps from the number of days of the simulation
    if params['fclen_units'] == 'days':
      num_timesteps = (int(params['fclen']) * 86400)/int(timestep)
      print("timestep: "+str(timestep))
      print("num_timesteps: "+str(num_timesteps))
      print("fclen: "+str(int(params['fclen'])))
      num_hours = int(params['fclen']) * 24
      num_days = params['fclen']

      # Throw an error if not cleanly divisible
      if int(num_timesteps) != num_timesteps:
        raise ValueError('Length of simulation (in days) does not divide equally by timestep')
-
      # Set upload interval and number of uploads, upload_interval is the number of timesteps between uploads
      if upload_frequency == 'daily':
        upload_interval = num_timesteps / int(params['fclen'])
      elif upload_frequency == 'weekly':
        upload_interval = (num_timesteps / int(params['fclen'])) * 7
      elif upload_frequency == 'monthly':
        upload_interval = (num_timesteps / int(params['fclen'])) * 30
      elif upload_frequency == 'yearly':
        upload_interval = (num_timesteps / int(params['fclen'])) * 365

      # Throw an error if not cleanly divisible
      if int(upload_interval) != upload_interval:
        raise ValueError('The number of time steps does not divide equally by the upload frequency')

    elif params['fclen_units'] == 'hours':
      num_timesteps = (int(params['fclen']) * 3600)/int(timestep)
      num_hours = int(params['fclen'])
      num_days = str('{0:.3f}'.format(int(params['fclen']) * 0.041666667)) # Convert to days and round to three decimals figures

      # Throw an error if not cleanly divisible
      if not(isinstance(num_timesteps,int)):
        raise ValueError('Length of simulation (in hours) does not divide equally by timestep')

          # Set upload interval and number of uploads, upload_interval is the number of timesteps between uploads
      if upload_frequency == 'hourly':
        upload_interval = num_timesteps / int(params['fclen'])

    number_of_uploads = int(math.ceil(float(num_timesteps) / float(upload_interval)))

    print("upload_interval: "+str(upload_interval))
    print("number_of_uploads: "+str(number_of_uploads))

    # Throw an error if not cleanly divisible
    if not(isinstance(number_of_uploads,int)):
      raise ValueError('The total number of timesteps does not divide equally by the upload interval')


    # Read in the namelist template file
    with open(project_dir+'oifs_workgen/namelist_template_files/'+namelist_template, 'r') as namelist_file :
        template_file = ''
        for line in namelist_file:
            # Replace the values
            line = line.replace('_EXPTID',params['exptid'])
            # Set the UMID as t000 to represent a test configuration
            line = line.replace('_UNIQUE_MEMBER_ID',start_umid)
            #  Do not replace these names as in the submiissioon script since they will be workunit dependent
            #line = line.replace('_IC_ANCIL_FILE',"ic_ancil_"+str(wuid))
            #line = line.replace('_IFSDATA_FILE',"ifsdata_"+str(wuid))
            #line = line.replace('_CLIMATE_DATA_FILE',"clim_data_"+str(wuid))
            line = line.replace('_HORIZ_RESOLUTION',horiz_resolution)
            line = line.replace('_VERT_RESOLUTION',vert_resolution)
            line = line.replace('_GRID_TYPE',grid_type)
            line = line.replace('_NUM_TIMESTEPS',str(num_timesteps))
            line = line.replace('_TIMESTEP',timestep)
            line = line.replace('_UPLOAD_INTERVAL',str(int(upload_interval)))
            line = line.replace('_ENSEMBLE_MEMBER_NUMBER',params['ensemble_member_number'])
            line = line.replace('_NUM_HOURS',str(num_hours))
            # Remove commented lines
            if not line.startswith('!!'):
                template_file=template_file+line

    # Read in the fullpos_namelist
    with open(ifs_ancil_dir+'fullpos_namelist/'+fullpos_namelist) as namelist_file_2:
        fullpos_file=''
        for line in namelist_file_2:
            if not line.startswith('!!'):
                fullpos_file=fullpos_file+line

    # Write out the workunit file, this is a combination of the fullpos and main namelists
    print("")
    print("fort.4 file for testing:")
    print("")
    print(fullpos_file)
    print(template_file)
