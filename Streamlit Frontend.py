import streamlit as st
import pandas as pd
import numpy as np
import os
import spacy
import time
import base64
from awsutils import AWSUtils
import logging
from botocore.exceptions import ClientError
import math
from Backend import nlpProc
import functools
import pikepdf
import pathlib
import PyPDF2

log=logging.getLogger(__name__)

s3BucketName = 'something'
s3TextractPrefix = 'something'

SEARCHABLEPDF_JAR_PTH = os.path.join("..", "bin", "searchable-pdf.jar")

nlp = spacy.load("en_core_web_sm")
fileID = ""

UPLOADPATH = os.path.join(".","uploads")
IMGPATH = os.path.join(".", "images")
TEXTRACTPATH = os.path.join(".", "textract_out")
RESULTPATH = os.path.join(".", "result")
this_directory = pathlib.Path().absolute()

comprehendList = {}

# #@st.cache
@st.cache(allow_output_mutation=True)
def get_process_state():
    """This dictionary is initialized once and can be used to store the preprocessing data"""
    return {}

#@st.cache(allow_output_mutation=True)
def nlpControls(xlsx_filename):
    
# STREAMLIT CONTROLS START #
        
    st.success('Analysis complete!') 
    href = f'<a href="#bottom" id="bottom">Start review here.</a>' #autoscrolls down one notch to review next section
    st.markdown(href, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files
    condition_processed = True
    condition_error = False
    st.write('\n')

    if condition_processed:        
        st.write('\n')
        st.header('3. Select')
#        st.write('\n')
        st.write('\n')
                
        df = pd.read_excel(xlsx_filename)

        df_fullname = df['Full Name'].to_list()
        df_DOB = df['Date of Birth'].to_list()
        df_ID = df['ID'].to_list()
        df_birthplace = df['Place of Birth'].to_list()
        df_gender= df['Gender'].to_list()
        
###        pd.options.display.float_format = '{:,.0f}'.format

        new_df_fullname = ''
        new_df_DOB = ''
        new_df_ID = ''
        
        def removeFloat(df_entity,new_df_entity): #remove float values from all dropdowns
            new_df_entity = []
            for item in df_entity: #need to use list method because not all entities in df are the same format, e.g. float can be mixed with alphabets in same row / column etc
                if isinstance(item, float):
                   if not math.isnan(item):
                        new_item = int(item)
                        new_df_entity.append(new_item)
                else:
                    new_df_entity.append(item)
            return new_df_entity
        
        new_df_fullname = removeFloat(df_fullname,new_df_fullname)
        new_df_DOB = removeFloat(df_DOB,new_df_DOB)
        new_df_ID = removeFloat(df_ID,new_df_ID)
        
# =============================================================================
#         df_fullname = df['Full Name'].dropna()
#         df_DOB = df['Date of Birth'].dropna()
#         df_ID = df['ID'].dropna()
#         
#         new_df_fullname = df_fullname.to_list()
#         new_df_DOB = df_DOB.to_list()
#         new_df_ID = df_ID.to_list()        
# 
# =============================================================================
       
        count_ID = 0
        
        for item in df_ID:
            if isinstance(item, float):
                if math.isnan(item):
                    count_ID += 1
        
        final_count_ID = len(df_ID) - count_ID
        
        count_DOB = 0
        
        for item in df_DOB:
            if isinstance(item, float):
                if math.isnan(item):
                    count_DOB += 1
        
        final_count_DOB = len(df_DOB) - count_DOB
        
        count = min(final_count_ID, final_count_DOB) #the default number of DOB and ID pairs to show
    
        full_numbers0 = list(np.arange(1, 100)) #give the option to choose to fill for up to 100 people        
        full_numbers = list(np.arange(1, 100)) #give the option to choose to fill for up to 100 people

        all_final_options0 = []        
        all_final_options = []
        
        no_blank = True
                        
        try:
          full_numbers.remove(count) #reorder the default number of people to the first value in dropdown list (because the selectbox widget doesn't have default value)
          full_numbers.insert(0, count)
          
        except ValueError:
          pass    
     
        option1 = st.selectbox('Select Total Pax.', full_numbers) #select total number of people details to fill and submit for the client
        st.write('\n')
        option0 = st.text_input('Key in Company Name:')#, value = optioned12) #no need default value
        st.write('\n')
        option2 = st.text_input('Key in Company Code:')#, value = optioned12) #no need default value
        st.write('\n')
        option3 = st.radio('Type of File(s)?', tuple(['ASL', 'DIR']), index = 0, key = 8000)
        st.write('\n')
        option4 = st.text_input('Starting Index for Individual (whole numbers only):')
        
        try:        
            if len(option4) > 0:
                option4 = int(option4)
                
        except ValueError:
            st.warning("""Please key in whole numbers only.""")
            st.write('\n')
            condition_error = True

        st.write('\n')
           
        option5 = st.text_input('Starting Index for Organisation (whole numbers only):')
        
        try:        
            if len(option5) > 0:
                option5 = int(option5)

        except ValueError:
            st.warning("""Please key in whole numbers only.""")
            condition_error = True
            
        st.write('\n')

        numbers = list(np.arange(1, int(option1)+1))

        st.write('\n')
            
        # start first function #
        
        optioned11 = ''
        optioned12 = ''
        optioned13 = ''
        
        def manualinput(options,optioned): #multi-entity, boolean value - if name, boolean value is true, use the concatenate method; if false, use original method
                                    
            if len(options) > 0: ####==1
                for thing in options: ####use index selection position 0
                    optioned = thing
                ######optioned = ' '.join(options)
                
            if len(options) == 0:
                optioned = ''
                                
            return optioned
        
        # end first function #
        
        for ix,position in enumerate(numbers):
            
            checked_condition_fullname = True
            checked_condition_DOB = True
            checked_condition_ID = True

            string23 = 'Which full name belongs to person ' + str(ix+1) + '?'
            string26 = 'Which date of birth belongs to person ' + str(ix+1) + '?'
            string27 = 'Which ID belongs to person ' + str(ix+1) + '?'
            string31 = 'Key in full name ' + str(ix+1) + ':'
            string32 = 'Key in date of birth ' + str(ix+1) + ':'
            string33 = 'Key in ID ' + str(ix+1) + ':'

            if ix < count: #fill default DOBs and IDs up to  min number of DOB and ID pairs
                
                string22 = 'Person ' + str(ix+1) +':'
        
                add_selectbox = st.sidebar.radio(string22, tuple(['Fill', 'Erase']), index = 0, key = 3000 + ix + 1)
            
                if add_selectbox == 'Fill':
                                            
                    st.write(string22)
                                  
                    #Full Name
                    
                    options11 = st.multiselect(string23, new_df_fullname)#, default = [new_df_fullname[ix+1]]) #can comment out default
                    optioned11 = manualinput(options11,optioned11)
                
                    if st.checkbox('Manually Input', key = 5000 + ix + 1):
                        options11 = st.text_input(string31, value = optioned11)
                        options11 = [(options11)]
                        checked_condition_fullname = False
                    
                    if checked_condition_fullname:
                        options11 = [(optioned11)]
                    
                    #Date of Birth
                    
                    by_default_DOB = []
                    
                    if len(new_df_DOB) > 0:
                        by_default_DOB.append(new_df_DOB[ix])
                        
                    options12 = st.multiselect(string26, new_df_DOB, default = by_default_DOB) #set default for DOBs for multiselect dropdown
                    optioned12 = manualinput(options12,optioned12)
                                
                    if st.checkbox('Manually Input', key = 7000 + ix + 1):
                        options12 = st.text_input(string32, value = optioned12)
                        options12 = [(options12)]
                        checked_condition_DOB = False
                    
                    if checked_condition_DOB:
                        options12 = [(optioned12)]
                    
                    #ID
                    
                    by_default_ID = []
                    
                    if len(new_df_ID) > 0:
                        by_default_ID.append(new_df_ID[ix])
                    
                    options13 = st.multiselect(string27, new_df_ID, default = by_default_ID) #set default for IDs for multiselect dropdown
                    optioned13 = manualinput(options13,optioned13)
                                
                    if st.checkbox('Manually Input', key = 9000 + ix + 1):
                        options13 = st.text_input(string33, value = optioned13)
                        options13 = [(options13)]
                        checked_condition_ID = False
                    
                    if checked_condition_ID:
                        options13 = [(optioned13)]

                    new_final_options0 = options11 + options12 + options13                  
                    new_final_options = options11 + [''] + ['I'] + [''] + options12 + [''] + [''] + [''] + [''] + [''] + options13
                    
                    all_final_options0.append(tuple(new_final_options0))                                
                    all_final_options.append(tuple(new_final_options))
                    
                    st.write('\n')
                    st.write('\n')    
                
                    if '' in new_final_options0:
                        no_blank = False
        
            else: #no default entities for entries that are more than min number of DOB and ID pairs
        
                string22 = 'Person ' + str(ix+1) +':'
        
                add_selectbox = st.sidebar.radio(string22, tuple(['Fill', 'Erase']), index = 0, key = 3000 + ix + 1)
                
                if add_selectbox == 'Fill':
                            
                    st.write(string22)
                    
                    #Full Name
                    
                    options11 = st.multiselect(string23, new_df_fullname)#, default = [new_df_fullname[ix+1]]) #no default
                    optioned11 = manualinput(options11,optioned11)
                    
                    if st.checkbox('Manually Input', key = 5000 + ix + 1):
                        options11 = st.text_input(string31, value = optioned11)
                        options11 = [(options11)]
                        checked_condition_fullname = False
                    
                    if checked_condition_fullname:
                        options11 = [(optioned11)]
                    
                    #Date of Birth
                    
                    options12 = st.multiselect(string26, new_df_DOB)#, default = [new_df_DOB[ix+1]]) #no default
                    optioned12 = manualinput(options12,optioned12)                
                
                    if st.checkbox('Manually Input', key = 7000 + ix + 1):
                        options12 = st.text_input(string32, value = optioned12)
                        options12 = [(options12)]
                        checked_condition_DOB = False
                    
                    if checked_condition_DOB:
                        options12 = [(optioned12)]
                        
                    #ID
                    
                    options13 = st.multiselect(string27, new_df_ID)#, default = [new_df_ID[ix+1]]) #no default
                    optioned13 = manualinput(options13,optioned13)                
                
                    if st.checkbox('Manually Input', key = 9000 + ix + 1):
                        options13 = st.text_input(string33, value = optioned13)
                        options13 = [(options13)]
                        checked_condition_ID = False
                    
                    if checked_condition_ID:
                        options13 = [(optioned13)]
                    
                    new_final_options0 = options11 + options12 + options13                  
                    new_final_options = options11 + [''] + ['I'] + [''] + options12 + [''] + [''] + [''] + [''] + [''] + options13
                    
                    all_final_options0.append(tuple(new_final_options0))                                
                    all_final_options.append(tuple(new_final_options))
                    
                    st.write('\n')
                    st.write('\n')    
                
                    if '' in new_final_options0:
                        no_blank = False
                    
        #href = f'<a href="#bottom" id="bottom">Review Data</a>'
        #st.markdown(href, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files
        st.header('4. Review')
        
        #horizontal alignment of radio buttons using html
        st.write('<style>div.Widget.row-widget.stRadio> div{flex-direction:row;}</style>', unsafe_allow_html=True)
        
        st.sidebar.markdown('\n\n')

        final_data0 = all_final_options0 #each inner list is a row #[([(a),(b),(c),'']),([(a),(b),(c),'']))]
        final_data = all_final_options #[] #each inner list is a row #[([(a),(b),(c),'']),([(a),(b),(c),'']))]

#
        
        data = []
        
        for tupled in all_final_options0:
            listed = list(tupled)
            for ind,thing in enumerate(listed):
                if thing == '':
                    listed[ind] = 'N.A.'
            data.append(listed)
        
        final_data_table = []
        
        for elements in data:
            new_ele = tuple(elements)
            final_data_table.append(new_ele)
        
        dfObj = pd.DataFrame(final_data_table, columns = ['Full Name' , 'Date of Birth', 'ID'])#, index=['a', 'b', 'c']) 
        dfObj.index = np.arange(1,len(dfObj)+1)
                
        front_case_ID = option2 + option3
        
        case_ID = []

        try:        
            if option5 < 10:
                option5 = '00' + str(option5)
            elif option5 > 9 and option5 < 100:
                option5 = '0' + str(option5)
        except TypeError:
            pass
            #st.warning("""Please key in whole numbers only.""")

        company_full_code = option2 + str(option5)

        try:        
            people_indexing = list(np.arange(option4, option4 + len(dfObj)))
            for index,item in enumerate(people_indexing):
                if item < 10:
                    item = '00' + str(item)
                elif item > 9 and item < 100:
                    item = '0' + str(item)
                case_ID.append(front_case_ID + str(item))
        
        except ValueError:
            pass
            #st.warning("""Please key in whole numbers only.""")
            
        except TypeError:
            pass
        
        step1 = [(option0)] + [(company_full_code)] + ['O'] + [''] + [''] + [''] + [''] + [''] + [''] + [''] + ['']
        step2 = tuple(step1)
                
        new_final_data = [step2] #[([(a),(b),(c),'']),([(a),(b),(c),'']))]

        for idx,element in enumerate(final_data):
            new_element = []
            for ix,item in enumerate(element):
                if ix == 1:
                    if len(case_ID) > idx:
                        item = case_ID[idx] #inserting case ID
                if ix == 3:
                    if len(df_gender) > idx:
                        item = df_gender[idx] #inserting gender                    
                if ix == 6:
                    if len(df_birthplace) > idx:
                        item = df_birthplace[idx] #inserting place of birth
                new_element.append(item)
            new_final_data.append(new_element)
            
        #st.write(new_final_data)
        st.dataframe(dfObj) #or st.table
        
        st.write('\n')                               
        st.write('\n')
                
        condition_ok = True
        condition_ok2 = True
        
        for tuples in final_data0:
            if len(tuples) != 3:
                condition_ok = False
        
        if not condition_ok or not no_blank:
            st.write('\n')
            st.warning("""Form may be incomplete.\n
       Please ensure you have reviewed every individual and/or filled all fields.""")
            if condition_error:
                st.warning("""Please key in whole numbers only.""")                
            condition_ok2 = False
            st.write('\n')
            # CSV File 1
            df = pd.DataFrame(final_data0, columns=["Full Name", "Date of Birth", "ID"])
            csv = df.to_csv(index=False, float_format=str)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
            href = f'<a download = "Client Details 1.csv" href="data:file/csv;base64,{b64}">Download CSV File 1</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
            new_href = 'Feel free to ' + href + '.'
            st.markdown(new_href, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files    
            # CSV File 2
            df2 = pd.DataFrame(new_final_data, columns=["Name*", 'Case ID', 'Entity Type*', 'Gender', "Date of Birth", 'Country of Residence', 'Place of Birth', 'Nationality', 'Registered Country', 'IMO Number', "Linked Entity Reference Number"])
            csv2 = df2.to_csv(index=False, float_format=str)
            b_64 = base64.b64encode(csv2.encode()).decode()  # some strings <-> bytes conversions necessary here
            href2 = f'<a download = "Client Details 2.csv" href="data:file/csv;base64,{b_64}">Download CSV File 2</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
            new_href2 = 'Feel free to ' + href2 + '.'
            st.markdown(new_href2, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files    
        
        if condition_ok and no_blank and len(final_data0) < option1:
            if condition_ok2:
                st.write('\n')
                st.warning("""Form may be incomplete.\n
                   Please ensure you have reviewed every individual and/or filled all fields.""")
                if condition_error:
                    st.warning("""Please key in whole numbers only.""")                               
                st.write('\n')
                # CSV File 1
                df = pd.DataFrame(final_data0, columns=["Full Name", "Date of Birth", "ID"])
                csv = df.to_csv(index=False, float_format=str)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
                href = f'<a download = "Client Details 1.csv" href="data:file/csv;base64,{b64}">Download CSV File 1</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
                new_href = 'Feel free to ' + href +'.'
                st.markdown(new_href, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files
                # CSV File 2
                df2 = pd.DataFrame(new_final_data, columns=["Name", 'Case ID', 'Entity Type', 'Gender', "Date of Birth", 'Country of Residence', 'Place of Birth', 'Nationality', 'Registered Country', 'IMO Number', "Linked Entity Reference Number"])
                csv2 = df2.to_csv(index=False, float_format=str)
                b_64 = base64.b64encode(csv2.encode()).decode()  # some strings <-> bytes conversions necessary here
                href2 = f'<a download = "Client Details 2.csv" href="data:file/csv;base64,{b_64}">Download CSV File 2</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
                new_href2 = 'Feel free to ' + href2 + '.'
                st.markdown(new_href2, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files    
            
        if condition_ok and no_blank and len(final_data0) >= option1 and not condition_error:
            st.write('\n')
            st.header('Success!')
            st.write('\n')
            st.success('You are all set!')
            st.write('\n')
            # CSV File 1
            df = pd.DataFrame(final_data0, columns=["Full Name", "Date of Birth", "ID"])
            csv = df.to_csv(index=False, float_format=str)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
            href = f'<a download = "Client Details 1.csv" href="data:file/csv;base64,{b64}">Download CSV File 1</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
            st.markdown(href, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files
            # CSV File 2
            df2 = pd.DataFrame(new_final_data, columns=["Name", 'Case ID', 'Entity Type', 'Gender', "Date of Birth", 'Country of Residence', 'Place of Birth', 'Nationality', 'Registered Country', 'IMO Number', "Linked Entity Reference Number"])
            csv2 = df2.to_csv(index=False, float_format=str)
            b_64 = base64.b64encode(csv2.encode()).decode()  # some strings <-> bytes conversions necessary here
            href2 = f'<a download = "Client Details 2.csv" href="data:file/csv;base64,{b_64}">Download CSV File 2</a>'# (click, then rename downloaded file such that it is &lt;name&gt;.csv)'
            new_href2 = 'Feel free to ' + href2 + '.'
            st.markdown(new_href2, unsafe_allow_html=True) #previous line - can save as csv, slk, dif files    
                    
# STREAMLIT CONTROLS END #
    
#@st.cache
@st.cache(allow_output_mutation=True)
def get_static_store():
    """This dictionary is initialized once and can be used to store the files uploaded"""
    return {}
# #@st.cache
@st.cache(allow_output_mutation=True)
def get_process_state():
    """This dictionary is initialized once and can be used to store the preprocessing data"""
    return {}
 
def cache_on_button_press(label, **cache_kwargs):
    """Function decorator to memoize function executions.
    Parameters
    ----------
    label : str
        The label for the button to display prior to running the cached funnction.
    cache_kwargs : Dict[Any, Any]
        Additional parameters (such as show_spinner) to pass into the underlying @st.cache decorator.
    Example
    -------
    This show how you could write a username/password tester:
    >>> @cache_on_button_press('Authenticate')
    ... def authenticate(username, password):
    ...     return username == "buddha" and password == "s4msara"
    ...
    ... username = st.text_input('username')
    ... password = st.text_input('password')
    ...
    ... if authenticate(username, password):
    ...     st.success('Logged in.')
    ... else:
    ...     st.error('Incorrect username or password')
    """
    internal_cache_kwargs = dict(cache_kwargs)
    internal_cache_kwargs['allow_output_mutation'] = True
    internal_cache_kwargs['show_spinner'] = False
    
    def function_decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            @st.cache(**internal_cache_kwargs)
            def get_cache_entry(func, args, kwargs):
                class ButtonCacheEntry:
                    def __init__(self):
                        self.evaluated = False
                        self.return_value = None
                    def evaluate(self):
                        self.evaluated = True
                        self.return_value = func(*args, **kwargs)
                return ButtonCacheEntry()
            cache_entry = get_cache_entry(func, args, kwargs)
            if not cache_entry.evaluated:
                if st.button(label):
                    cache_entry.evaluate()
                else:
                    raise st.ScriptRunner.StopException
            return cache_entry.return_value
        return wrapped_func
    return function_decorator

def createResources():
    try:
        for path in [IMGPATH, TEXTRACTPATH, UPLOADPATH, RESULTPATH]:
            if os.path.isdir(path) is not True:
                os.mkdir(path)
    except:
        print("Failed to create resources")
        
def writeToDrive(static_store, sessionID):
    st.write("Pre-processing...")
    docList = []
    for idx, value in enumerate(static_store.values()):
        docPath =  os.path.join(UPLOADPATH, ("{}_{}.pdf").format(sessionID, str(idx)))        
        docPath0 =  os.path.join(UPLOADPATH, ("{}_{}.pdf").format(sessionID, str(idx)))        
        try:
            with open(docPath, "wb") as upf:
                upf.write(value)
                reader = PyPDF2.PdfFileReader(upf)
                reader.getNumPages() #DETECT IF PDF IS PASSWORD PROTECTED - IF YES, ERROR 'PdfReadError: File has not been decrypted' IS THROWN                
            docList.append(docPath)            

        except:
            option00 = st.text_input('Input Password:')    
    #        pdf = pikepdf.open(docPath2)
            final_path = "L:\\My Documents\\Desktop\\CSA\\Demo for Distribution - 12 Jun\\unlocked.pdf" #CHANGE THIS TO A GENERIC FILE PATH
    #        pdf.save(final_path)
            ##with pikepdf.open(docPath2, password="Bi@2018"):# as pdf:
            ##pikepdf.Pdf.open(docPath2, password='Bi@2018')
            with pikepdf.open(docPath0, password = option00) as pdf:
                pdf.save(final_path)
# =============================================================================
#             pdf = pikepdf.open(docPath0, password = option00)
#             pdf.save(final_path)
# =============================================================================
            with open(final_path, "wb") as f:
                f.write(value)
            st.write("Loading...")
            #st.warning("""Error processing document.\n
            #         Please disable password protection before processing.""")
            docList.append(final_path)       
    return docList
# @cache_on_button_press('Process File(s)')

#@st.cache(hash_funcs={io.StringIO: io.StringIO.getvalue}, suppress_st_warning=True)
def preproc(docList, aws):
    rList = []
    try:
        for index,doc in enumerate(docList):
#            st.write("Uploading...")
            aws.uploadFile(s3BucketName, doc, '{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            if index == 0:
                st.write("Running OCR...")
            jobid = aws.startTextractJob(s3BucketName,'{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            if jobid and aws.isTextractJobComplete(jobid):
                if index == 0:
                    st.write("Running NLP...")
                response = aws.getTextractJobResults(jobid)
                ######print(response)
                ######st.write(aws.printTextractResponse(response))
                rList.append(response)
                aws.deleteFile(s3BucketName, '{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            st.write('\n')
    except ClientError as e:
        logging.error(e)     
    
    return rList

def preproc2(docList, aws):
    rList = []
    try:
        for index,doc in enumerate(docList):
#            st.write("Uploading...")
            aws.uploadFile(s3BucketName, doc, '{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            #if index == 0:
                #st.write("Running OCR...")
            jobid = aws.startTextractJob(s3BucketName,'{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            if jobid and aws.isTextractJobComplete(jobid):
                #if index == 0:
                    #st.write("Running NLP...")
                response = aws.getTextractJobResults(jobid)
                ######print(response)
                ######st.write(aws.printTextractResponse(response))
                rList.append(response)
                aws.deleteFile(s3BucketName, '{}/{}'.format(s3TextractPrefix, os.path.basename(doc)))
            st.write('\n')
    except ClientError as e:
        logging.error(e)     
    
    return rList

def processDoc(static_store, sessionID, aws):
    excelPath = ''
    docList = writeToDrive(static_store, sessionID)
    rList = preproc(docList, aws) #1 - this is run the number of times the equivalent number of files there are
    #st.write("Starting NLP analysis...")
    excelPath = nlpProc(rList) #2
    ##########st.write(rList) # TEST PRINT TO CHECK WHAT GOES INTO NLPPROC
    return excelPath, rList
    
def main():
    createResources()

    aws = AWSUtils.getInstance()
    sessionID = int(str(time.time()).replace('.', ''))

    st.title("World Check Screening")
    st.subheader("POC for Distribution - Client Services")
    st.write ('\n')
    st.write ('\n')
    
    processState = get_process_state()
    static_store = get_static_store()    

    full_numbers = list(np.arange(1, 30)) #select up to 30 files to upload at a go

    st.header('1. Upload')
    st.write ('\n')
        
    no_of_people = st.selectbox('Select No. of Files', full_numbers)
        
    excelPath = ''
    
    # BROWSE FILE STARTS #
    
    result = st.file_uploader("Upload Files", type="pdf") #'result' type is <class '_io.BytesIO'>
    condition_nofile = False
   
    if result:
        #static_store.clear()
        # Process your file here
        value = result.getvalue()

        # And add it to the static_store if not already in
        if not value in static_store.values():
            static_store[result] = value
        
        if st.button("Clear Files"):
            static_store.clear()
            condition_nofile = True
            processState.clear()
                
    if not result:
        static_store.clear()  # Hack to clear list if the user clears the cache and reloads the page
        #st.info("Upload exactly one `.pdf` file.")
             
    store = static_store.keys()
    listed = list(store)
    to_print = 'No. of files uploaded: ' + str(len(listed))
    st.write(to_print)
    
    if result and not condition_nofile:
        st.info('Clear files first if browsing again.')

    st.write('\n')
    st.write('\n')
        
    # BROWSE FILE ENDS #
                    
    if len(list(static_store.keys())) == no_of_people: 
        
        st.header('2. Process')
        st.write('\n')

        if not condition_nofile:
            # processState = get_process_state()
            print('before processing: {}'.format(len(processState)))
        
            if len(processState) == 0:
                excelPath, rList = processDoc(static_store, sessionID, aws)
                # Process you file here
                if excelPath:
                    processState[excelPath] = rList
                    print("state1:{}".format(len(processState)))
                    nlpControls(excelPath)
                
            else:
                nlpControls(list(processState.keys())[0])
    
if __name__ == '__main__':
    main()
