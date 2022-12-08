#! /usr/bin/env python

# Program : create_xml_funcs.py
# Author  : Sarah Sparrow modified from CPDN script.
# Purpose : functions for creating the openifs xml.

from xml.etree.ElementTree import *
from ANC import *
from xml.dom import minidom

# Sampling imports
import openturns as ot

from socket import gethostname

host=gethostname()
if host=='caerus' or host =='hesperus':
	project_dir='/storage/www/cpdnboinc/'
elif host=='pandia':
	project_dir='/storage/www/cpdnboinc_dev/'

def CreateSampling(para_per,para_bou,n_ens):
    # Verify the size of the name and boundary of perturbed parameters:
    assert len(para_per) == len(para_bou), "Sensitivity: the number of parameters and boundaries are inconsistent."

    # Create the PDF:
    list_distrib = []
    for bounds in para_bou:
        # Create Dirac PDF for Integer:
        if bounds[:1] == "I":
            boundaries = bounds[1:].split(";")
            number_integer = 1 + int(boundaries[1]) - int(boundaries[0])
            samples = []
            prob = []
            for i in range(int(boundaries[0]), 1 + int(boundaries[1])):
                samples.append([float(i)])
                prob.append(1/number_integer)
            sample = ot.Sample(samples)
            points = ot.Point(prob)
            list_distrib.append(ot.UserDefined(sample,points))
        # Create Uniform PDF for Float:
        elif bounds[:1] == "F":
            boundaries = bounds[1:].split(";")
            list_distrib.append(ot.Uniform(float(boundaries[0]), float(boundaries[1])))
        else:
            raise Exception("Wrong type identifier in boundaries: only I and F are accepted.")

    # Create the composite distribution:
    distribution = ot.ComposedDistribution(list_distrib)
    distribution.setDescription(para_per)

    # Create the LHS sampling:
    experiment = ot.LHSExperiment(distribution, n_ens)
    out_table = experiment.generate()

    return out_table

def get_upload_info(upload_loc):
    # Dictionary of upload file handlers
    upload_info_dict={"alpha":("alpha","http://alpha.cpdn.org/cgi-bin/file_upload_handler"),
                      "dev":("dev","https://dev.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload2":("upload2","http://upload2.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload3":("upload3","http://upload3.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload4":("upload4","http://upload4.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload5":("upload5","http://upload5.cpdn.org/cpdn_cgi_main/file_upload_handler"),
                      "upload6":("upload6","http://upload6.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload7":("upload7","http://upload7.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload8":("upload8","http://upload8.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload9":("upload9","http://upload9.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload10":("upload10","http://upload10.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload11":("upload11","http://upload11.cpdn.org/cgi-bin/file_upload_handler"),
                      "upload12":("upload12","http://upload12.cpdn.org/cgi-bin/file_upload_handler")}

    upload_handler=upload_info_dict[upload_loc][1]
    upload_template="upload_templates/"+upload_info_dict[upload_loc][0]+"/result_template_oifs"

    return upload_handler,upload_template

# Take dictionary of parameters and add experiment to the xml
def CreateWorkunit(params, ic_ancil,ifs_data,climate_data,sens_exp,parameters):
    # Set experiment and parameters tags and add to document
    Workunit=Element('workunit')
    WU_tree=ElementTree(Workunit)
    # Loop over parameters and add
    for param,value in sorted(params.items()):
        SubElement(Workunit, param).text=str(value)
	
    # Add perturbed parameters
    if sens_exp:
        pp=Element('parameters')
        pp_tree=ElementTree(pp)
        for param,value in sorted(parameters.items()):
            SubElement(pp, param).text=str(value)	

    # Add initial data file
    ica=Element('ic_ancil')
    ica_tree=ElementTree(ica)
    for param,value in sorted(ic_ancil.items()):
        SubElement(ica, param).text=str(value)	
	
	# Add ifs_data files
    ifsd=Element('ifsdata')
    ifsd_tree=ElementTree(ifsd)
    for param,value in sorted(ifs_data.items()):
        SubElement(ifsd, param).text=str(value)
        
    # Add climate_data files
    clid=Element('climate_data')
    clid_tree=ElementTree(clid)
    for param,value in sorted(climate_data.items()):
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
    for param,value in sorted(batch.items()):
        SubElement(binf, param).text=str(value)

    SubElement(binf, 'workunit_range').text="workunit_range"
    SubElement(binf, 'batchid').text="batchid"
    return binf

def CreateFort4(params,dates,s_ens,start_umid,model_config,fullpos_namelist):
    # Set some paths to find the config file and 
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
        sfac=86400
        hfac=24
    elif params['fclen_units'] == 'hours':
        sfac=3600
        hfac=1
    
    num_timesteps = (int(params['fclen']) * sfac)/int(timestep)
    num_hours=int(params['fclen']) * hfac
    num_days=num_hours/24.

    # Throw an error if not cleanly divisible
    if not(isinstance(num_timesteps,int)):
        raise ValueError('Length of simulation does not divide equally by timestep')

    # Set upload interval and number of uploads, upload_interval is the number of timesteps between uploads
    if upload_frequency == 'daily':
        upload_interval = num_timesteps / num_days
    elif upload_frequency == 'weekly':
        upload_interval = (num_timesteps / num_days) * 7
    elif upload_frequency == 'monthly':
        upload_interval = (num_timesteps / num_days) * 30
    elif upload_frequency == 'yearly':
        upload_interval = (num_timesteps / num_days) * 365

    # Throw an error if not cleanly divisible
    if not(upload_interval.is_integer()):
        raise ValueError('The number of time steps does not divide equally by the upload frequency')
    
    number_of_uploads = int(num_timesteps/upload_interval)
    #number_of_uploads = int(math.ceil(float(num_timesteps) / float(upload_interval)))
    print("")
    print("Upload Interval (number of timesteps between uploads): "+str(int(upload_interval)))
    print("Number of uploads: "+str(number_of_uploads))

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
