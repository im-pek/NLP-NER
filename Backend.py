import os
import os.path
from os import path
import json
from datetime import datetime
import itertools
from itertools import permutations
import spacy
from nltk import word_tokenize, pos_tag, ne_chunk
import fileinput
import sys
import csv
import pandas as pd
import enchant
import string
import pathlib
from long_lists import all_surnames, en_names, indonesia_cities, text_to_remove

def nlpProc(rList):
    
    dateTimeObj = datetime.now()
    dateObj = dateTimeObj.date()
    dateStr = dateObj.strftime("%d %b %Y ") #current date to label output file

    time = str(dateTimeObj.hour) + '`' + str(dateTimeObj.minute) + '`' + str(dateTimeObj.second) #current time to label output file
    
    this_directory = pathlib.Path().absolute() #directory path of where this python file is saved

    __DOBs = []
    all_texts= []
    all_possible_IDs = []    
    joined_final_names = []
    first_names = []
    last_names = []
    final_DOBs = []
    final_DOBs2 = []    
    finalised_IDs = []   
    all_get_text = []

#    condition_isBrunei = False

    # =============================================================================
    # for doc in rList:
    #     for pg in rList[doc]:
    #         json
    #     
    # rList: [[DOC1],[DOC2]]
    # 
    # DOC1: [ pg1[{tezxtract json}], pg2[]]
    # =============================================================================
        
    for doc in rList:
        text_length = 0
        all_get_text_inner = []

        for json_dict in doc: #json_dict = page
            if 'Blocks' in json_dict:
                blocks = json_dict['Blocks']
                for dicti in blocks:
                    if dicti.get('BlockType') == 'LINE':
                        if dicti.get('Text') != None:
                            a_text = dicti['Text']
                            all_get_text_inner.append(a_text)
                            text_length += 1                
                        
        all_get_text.append([all_get_text_inner, text_length])
    
    # PROCESS ASLs BEFORE PROCESSING IDs BY ORDERING THE ASLs FIRST (AS WE ASSUME ASLs HAVE LONGER TEXT LENGTH), i.e. DOCUMENTS ORDERED FROM LONGEST TO SHORTERST TEXT LENGTH #
    
    # take second element for sort
    def takeSecond(elem):
        return elem[1]
        
    # sort list with key
    all_get_text.sort(key=takeSecond, reverse=True)
    
    final_all_get_text = []
    
    for element in all_get_text:
        for more in element[0]:
            final_all_get_text.append(more)
            
##### 1: Remove pre-defined fixed words (fixed words in IDs) #####
            
    def removefixedwords(finalallgettext):
        
        birthcountry = []
        alltexts= []    
        draft_all_texts = ''
        gender = []

        for get_text in finalallgettext: #get_text is a page                    
            get_text = get_text.replace('$','S')
            text_tokens = word_tokenize(get_text)
            tokens_without_sw = [word for word in text_tokens if not word in text_to_remove]
            get_text = ' '.join(tokens_without_sw)

            for city in indonesia_cities:
                capitalise_city = string.capwords(city)
                get_text = get_text.replace(capitalise_city,'')  

            #it is possible that indonesia has more cities (to remove) - currently found       
                                        
            #def count_occurrences(word, sentence):
            #    return sentence.split().count(word)
            
            count_singapore = 0
            
            if 'SINGAPORE' in get_text:
                count_singapore += 1
 
            if count_singapore == 2: #detect if place of birth is Singapore
                birthcountry.append('Singapore')
           
            if 'F' in get_text: #detect if female
                gender.append('Female')
            
            if 'M' in get_text: #detect if male
                gender.append('Male')
            
#            if 'Malaysia' in get_text: #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH
#                birthcountry.append('Malaysia') #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH

#            if 'Brunei' in get_text: #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH
#                birthcountry.append('Brunei') #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH

#            if 'Thai' in get_text: #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH
#                birthcountry.append ('Thailand') #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH

#            if 'Indonesia' in get_text or 'Provinsi' in get_text: #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH
#                birthcountry.append('Indonesia') #UNCOMMENT IF COUNTRY OF CARD ISSUANCE IS PLACE OF BIRTH
                                
            #if get_text == 'Brunei':
                #condition_isBrunei = True
            
##### 2: Extract IDs (min. length 6, alphanumeric, numeric) ##### PUT INTO FUNCTION IF POSSIBLE
        
            for_checking_get_text = ''.join(e for e in get_text if e.isalnum())
            
            possible_IDs_mix = []
            possible_IDs_num = []
                    
                    
            if not for_checking_get_text.isalpha():
                if not for_checking_get_text.isnumeric():
                    if get_text not in possible_IDs_mix:
                        possible_IDs_mix.append(get_text)
            if for_checking_get_text.isnumeric():
                if get_text not in possible_IDs_num:
                    possible_IDs_num.append(get_text)
            
            possible_IDs = possible_IDs_mix + possible_IDs_num
            
            for item in possible_IDs:
                if len(item) > 5: #CHANGE THIS DEPENDING ON DESIRED MINIMUM LENGTH OF ID (SYMBOLS, ALPHABETS, NUMBERS ALL INCLUSIVE)
                    split_item = item.split()
                    for elem in split_item:                        
                        for_IDs_elem = elem.translate(str.maketrans('', '', string.punctuation))
                        
                        
                        if len(for_IDs_elem) > 5: #CHANGE THIS DEPENDING ON DESIRED MINIMUM LENGTH OF ID (SYMBOLS, ALPHABETS, NUMBERS ALL INCLUSIVE)
                            if not for_IDs_elem.isalpha():
                                if for_IDs_elem not in all_possible_IDs:
                                    all_possible_IDs.append(for_IDs_elem)
                        
                        if len(for_IDs_elem) > 5: #CHANGE THIS DEPENDING ON DESIRED MINIMUM LENGTH OF ID (SYMBOLS, ALPHABETS, NUMBERS ALL INCLUSIVE)                 
                            if for_IDs_elem.isnumeric():
                                if item not in all_possible_IDs:
                                    all_possible_IDs.append(item)
                                    
    #print ('\n')
    #print (all_possible_IDs)          
            
            if '19' in get_text:
                new_get_text = get_text.replace('-',' ')
                new_get_text = new_get_text.replace('/',' ')
                __DOBs.append(new_get_text)
            
            if get_text not in draft_all_texts:
                if get_text not in all_possible_IDs:
                    alltexts.append(get_text)
                    draft_all_texts += ' ' + get_text
    
        return alltexts, birthcountry, gender
        
    def textpreprocessing1(every_texts):
        
        all__texts = []
        
        for item in every_texts:
            splits = item.split()
            new_item = ''
            for ix,elem in enumerate(splits):
                new_element = elem.capitalize()
                if ix == 0:
                    new_item += new_element
                if ix > 0:
                    new_item += ' ' + new_element
            all__texts.append(new_item)
        
        finalalltexts = []
            
        for stringed in all__texts:
            translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space    
            new_stringed = stringed.translate(translator)
            finalalltexts.append(new_stringed)
        
        print ('ALL TEXTS', finalalltexts)
        print ('\n')
        
        text =' '.join(finalalltexts)
        
        #print (text)
        #print ('\n')
        
        #no punctuation version of original text
            
        translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space    
        no__punc__text = text.translate(translator)
        
        print ('NO PUNC TEXT', no__punc__text)
        print ('\n')
        
        return no__punc__text, finalalltexts
    
        
##### 3: spaCy to do Named Entity Recognition (NER) to remove locations #####

    def spacyNER(nopunctext):
               
        #Spacy to remove GPE, LANGUAGE, LOC
        #text is the original text
        
        nlp = spacy.load('en_core_web_sm')
                
        classify = nlp(nopunctext)
        
        entities=[(i, i.label_, i.label) for i in classify.ents]
        
        #print (entities)
        
        list_remove=[]
        
        for item in entities:
            condition = False
            if item[1] == 'GPE' or item[1] == 'LANGUAGE' or item[1] == 'LOC':
                condition = True
            if condition:
                list_form=list(item)
                to_remove=str(list_form[0])
                list_remove.append(to_remove)
        
        worded_form = nopunctext.split()
        
        #print (worded_form)
        
        no_locations = []
        
        for element in worded_form:
            if element not in list_remove:
                no_locations.append(element)
        
        #print (no_locations)
        
        new__text = []
        
        for item in no_locations:
            if item not in new__text:
                new__text.append(item)
                
        newtext = ' '.join(new__text)
        
        return newtext
    
    #print (new_text)
    
    #remove consonant-only words
    
    def textpreprocessing2(news_text):
        
        approved_words = []
        
        _new__text = news_text.split()
        
        for word in _new__text:
            if word.isnumeric():
                approved_words.append(word)
            if word.isalnum():
                if not word.isalpha():
                    if not word.isnumeric():
                        approved_words.append(word)
            if word.isalpha():
                for char in word:
                    if char in 'aeiouAEIOU':
                        if word not in approved_words:
                            approved_words.append(word)
        
        new_text = ' '.join(approved_words)
        
        #print (new_text)
            
        #NLTK to identify English and anglicised Asian names
                
        list_output = list(ne_chunk(pos_tag(word_tokenize(new_text))))
        
        #print (list_output)
        #print ('\n')
        
        new_output=[]
        
        for item in list_output:
            list_item=list(item)
            new_output.append(list_item)
        
        #print (new_output)
        
        neww_output=[]
        
        for listed in new_output:
            listt=[]
            for bracket in listed:
                if type(bracket) == tuple:
                    listed_bracket=list(bracket)
                    listt.append(listed_bracket)   
                else:
                    listt.append(bracket)
            neww_output.append(listt)
        
        #print (neww_output)
        #print ('\n')
        
        double_apostrophe = json.dumps(neww_output)
        
        final_pairs_string = str(double_apostrophe)
        
        #print (final_pairs_string)
                
        #segregate names
        
        final_pairs_string = str(final_pairs_string)
        
        txt_out = str(this_directory) + '\out.txt'
        csv_out = str(this_directory) + '\out.csv'
        
        text_file_1 = open(txt_out, "w")
        text_file_1.write("%s" % final_pairs_string)
        text_file_1.close()
        
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace('[', ''))
        
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace(']', ''))
            
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace('(', ''))
        
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace(')', ''))
            
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace('"', ''))
        
        for i, line in enumerate(fileinput.input(txt_out, inplace=1)):
            sys.stdout.write(line.replace(', ', ','))
        
        if path.exists(csv_out):
            os.remove(csv_out)
        os.rename(txt_out, csv_out)
        
        with open(csv_out, 'r') as inputfile:
            readers = csv.reader(inputfile)
            output_1 = list(readers)
        
        a_list_output_1 = []
        
        for thing in output_1:
            for things in thing:
                a_list_output_1.append(things)
                
        #print (a_list_output_1)
        
        filtered = list(filter(None, a_list_output_1))
        
        #print (filtered)
        #print ('\n')
        
        def divide_chunks(l, n):
            # looping till length l
            for i in range(0, len(l), n):  
                yield l[i:i + n]
        
        xx = list(divide_chunks(filtered, 2))
        
        return xx
        
    #print (x)
    #print ('\n')

##### 4: NLTK to classify nouns, verbs, adjectives (use nouns) #####
    
    def nltkNER(x):
    
        independent__names = []
        all_fresh_names = []
        
        for idx,item in enumerate(x):
            fresh_names = []
            if idx == 0:
                if 'NNP' in item:
                    if 'NNP' in x[idx+1]:
                        fresh_names.append(x[idx][0])
                    else:
                        independent__names.append(x[idx][0])
            if idx > 0 and idx < len(x)-1:
                if 'NNP' in item:
                    if 'NNP' not in x[idx-1] and 'NNP' in x[idx+1]:
                        fresh_names.append(x[idx][0])
                    if 'NNP' in x[idx-1]:
                        fresh_names.append(x[idx][0])
                    if 'NNP' not in x[idx-1] and 'NNP' not in x[idx+1]:
                        independent__names.append(x[idx][0])
            all_fresh_names.append(fresh_names)
        
        ready_for_en_removal = []
        
        for names in all_fresh_names:
            if len(names) != 0:
                ready_for_en_removal.append(names)
            if len(names) == 0:
                ready_for_en_removal.append(['---'])
        
        segregated___names = []
        
        for listed in ready_for_en_removal:
            for item in listed:
                segregated___names.append(item)
        
        return segregated___names,independent__names
        
    #print (segregated_names)
    #print ('\n')
    #print (independent_names)
        
    #EXTRACT FIRST NAMES, LAST NAMES (includes anglicised english names)    
    #REMOVE ALL ENGLISH WORDS (and standalone numbers) FOUND IN ENGLISH DICTIONARY, EXCEPT NORMAL ENGLISH NAMES
    
    def full_names(segregates_names,independents_names):

##### 5: Enchant to identify English words (UK and US dictionaries) #####
##### 6: data.world to get list of English first names (already in list, 'en_names') #####

        us = enchant.Dict("en_US")
        uk = enchant.Dict("en_UK")
                
        en_to_remove=[]
                
        for ix,item in enumerate(segregates_names):
            if item == True or item == False:
                segregates_names.pop(ix)
        
        for ix,word in enumerate(segregates_names):
            if us.check(word) or uk.check(word):
                if word not in en_names: #AN ENGLISH WORD THAT IS NOT AN ENGLISH NAME
                    en_to_remove.append(ix)
        
        #print (en_to_remove)
    
##### 7: Remove all English words that are not English first names #####
        
        for item in en_to_remove:
            segregates_names[item]=''
        
        #print (segregates_names)
        
        filteredsets = list(filter(None, segregates_names))
        
        #print (filteredsets)
        #print ('\n')
        
        for idx,item in enumerate(filteredsets):
            if item == '---':
                filteredsets[idx] = ''
        
        filtereddsets = '_'.join(filteredsets)
        
        #print (filtereddsets)
        #print ('\n')
        
        new_string = ''
        
        for ix,char in enumerate(filtereddsets):
            if ix > 0 and ix < len(filtereddsets)-1:
                if char == '_':
                    if filtereddsets[ix-1] == '_' or filtereddsets[ix+1] == '_':
                        char = ' '
            if char == '_':
                if ix == 0:
                    if filtereddsets[ix+1] == '_':
                        char = ' '
            if char == '_':
                if ix == len(filtereddsets)-1:
                    if filtereddsets[ix-1] == '_':
                        char = ' '
            new_string += char
        
        #print (new_string)
        #print ('\n')
        
        full_segregated_names = new_string.split()
        
        #print (full_segregated_names)
        #print ('\n')
        
        fulled_segregated_names = []
        
        for item in full_segregated_names:
            items = item.split('_')
            fulled_segregated_names.append(items)
        
        fulls_segregated_names = []
        
        for elem in fulled_segregated_names:   
            appent = list(filter(None, elem))
            fulls_segregated_names.append(appent)
            
        #print (fulls_segregated_names)
        
##### 8: Non-English names (common in SEA) and English names remain #####
        
        #EXTRACT INDEPENDENT NAMES
        
        en_to_remove_2=[]
        
        for ix,item in enumerate(independents_names):
            if item == True or item == False:
                independents_names.pop(ix)
        
        for ix,word in enumerate(independents_names):
            if us.check(word) or uk.check(word):
                if word not in en_names: #AN ENGLISH WORD THAT IS NOT AN ENGLISH NAME
                    en_to_remove_2.append(ix)
        
        #print (en_to_remove)
        
        for item in en_to_remove_2:
            independents_names[item]=''
        
        #print (independents_names)
        
        filteredsets2 = list(filter(None, independents_names))
        
        #print (filteredsets2)
        
        for name in filteredsets2:
            fulls_segregated_names.append([name])
        
        #print (fulls_segregated_names)
                
        finalised_full_names = []
        
        for names in fulls_segregated_names:
            for item in names:
                #print ('ITEM', item)
                for elem in final_all_texts:
                    #print ('ELEM', elem)
                    if item in elem:
                        finalised_full_names.append(elem)
                    else:
                        if item not in finalised_full_names:
                            finalised_full_names.append(item)
                        
        en_to_remove1 = []
            
        for ix,name in enumerate(finalised_full_names):
            split_name = name.split()
            for indiv in split_name:
                if us.check(indiv) or uk.check(indiv):
                    if indiv not in en_names:
                        if indiv not in all_surnames: #AN ENGLISH WORD THAT IS NOT AN ENGLISH NAME
                            en_to_remove1.append(ix)
        
        for item in en_to_remove1:
            finalised_full_names[item]=''
                        
        finalised_full_names = [x for x in finalised_full_names if x]
        finalised_full_names = list(dict.fromkeys(finalised_full_names))
        
        def num_there(s):
            return any(i.isdigit() for i in s)
        
        final_full_names = []
        
        for item in finalised_full_names:
            if num_there(item) == False:
                final_full_names.append(item)
        
        #print ('FINAL FULL NAMES', final_full_names)    
        #print ('\n')
                
        duplicated_final_full_names = final_full_names
        
        all_matching = []
        
        for thing in duplicated_final_full_names:
            for another in final_full_names:
                if thing in another:              
                    if thing != another:
                        all_matching.append(another)
        
        all_matching = list(dict.fromkeys(all_matching))
            
        new_all_matching = all_matching
        
        for thing in duplicated_final_full_names:
            if any(thing in s for s in all_matching):
                pass
            else:
                new_all_matching.append(thing)
        
##### 9: Any Chinese surname is moved to the back of Full Name #####
        
        final_names = []
        
        for ix,item in enumerate(new_all_matching):
            names = item.split()
            if names[0] in all_surnames:
                names.append(names[0])
                del names[0]
                final_names.append(names)
            else:
                final_names.append(names)
        
        #print ('\n')           
        #print ('FINAL NAMES', final_names)
        #print ('\n')
            
        for naming in final_names:
            joined_name = ' '.join(naming)
            joined_final_names.append(joined_name) #final full names
            
        #print ('\n')           
        #print ('JOINED FINAL NAMES', joined_final_names)
        #print ('\n')
    
##### 10: First Name is derived from taking first to second last word in Full Name #####
##### 11: Last Name is derived from taking last word in Full Name #####
        
        all_first_name_last_name = []
        
        for naming in final_names:
            if len(naming) > 2:
                long_name = ' '.join(naming[:-1])
                all_first_name_last_name.append([long_name, naming[-1]])
            else:
                all_first_name_last_name.append(naming)
        
        #print ('\n')            
        #print ('all first name last name', all_first_name_last_name)
        #print ('\n')
        
        first_name_last_name = []
        
        for listed in all_first_name_last_name:
            if len(listed) == 1:
                listed.append('')
            first_name_last_name.append(listed)
            
        #print ('first name, last name', first_name_last_name)
            
        for pairs in first_name_last_name:
            first_names.append(pairs[0])
            last_names.append(pairs[1])
        
        print ('FINAL FIRST NAMES', first_names) #final first names
        print ('\n')
        print ('FINAL LAST NAMES', last_names) #final last names
        print ('\n')

        return joined_final_names, first_names, last_names
    
    #EXTRACT DATES OF BIRTH
    #All punctuations, including '-' and '/' that separates dates, would have already been removed in the very first tokenisation
    #People should be writing years in 4-digit format, if not client document would be invalid in the first place
            
##### 12: DOBs are identified whenever any combination of possible DOB is detected in text #####
    
    def DOBs(___DOBs):

        all_months_number = ['1','2','3','4','5','6','7','8','9','10','11','12','01','02','03','04','05','06','07','08','09','10','11','12']
        all_months_spelling = ['January','February','March','April','May','June','July','August','September','October','November','December','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        all_months = all_months_number + all_months_spelling
    
        days = list(range(1,32))
    
        day_permutations = days + ['01','02','03','04','05','06','07','08','09','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Ninth']
    
        all_days=[]
    
        for day in day_permutations:
            new_day = str(day)
            all_days.append(new_day)
    
        year_permutations = list(range(1850,2022))
    
        all_years = []
    
        for year in year_permutations:
            new_year = str(year)
            all_years.append(new_year)
    
        combinations = list(itertools.product(all_days, all_months, all_years))
    
        #print (combinations)
    
        all_perms_and_combs = []
    
        for sets in combinations:
            listed = list(sets)
            permuted = permutations(listed)
            all_perms_and_combs.append(permuted)
    
        #print (all_perms_and_combs) #comment this out, else bandwidth exceeds
    
        all_dates = []
    
        for date in all_perms_and_combs:
            for spec_date in date:
                all_dates.append(list(spec_date))
    
        full_dates = []
    
        for joint in all_dates:
            dates = ' '.join(joint)
            full_dates.append(dates)
        
        DOBs = []
        
        for a_date in full_dates:
            if ' '+a_date+' ' in no_punc_text:
                if a_date not in DOBs:
                    DOBs.append(a_date)    
        
        for date in ___DOBs:
            if date not in DOBs:
                DOBs.append(date)
                
        for item in DOBs:
            if len(item) > 5:
                split_item = item.split()
                check_joined = ''.join(split_item)
                for elem in split_item:
                    if check_joined.isnumeric():
                        if item not in final_DOBs2:
                            if len(item) < 13:
                                final_DOBs.append(item.replace(' ','/'))
                                final_DOBs2.append(item)                                
                    if elem in all_months_spelling:
                        if item not in final_DOBs2:
                            if len(item) < 13:
                                final_DOBs.append(item.replace(' ','/'))
                                final_DOBs2.append(item)                                
                
        #print (final_DOBs)
        
        for__validating = []
        
        for element in final_DOBs2:
            to_validate_ = element.split()
            to_validate = ''.join(to_validate_)
            for__validating.append(to_validate)
        
        print ('FINAL DOBs', final_DOBs)       
        print ('\n')
        
        return for__validating
    
    def IDs(alls_possible_IDs):
        
        final__IDs = list(dict.fromkeys(alls_possible_IDs))
        
        final_IDs = []
        
        for item in final__IDs:
            new_item = item.upper()
            for_checking = new_item.translate(str.maketrans('', '', string.punctuation))
            if for_checking not in for_validating:
                if for_checking not in final_IDs:
                    final_IDs.append(for_checking)
        
        for ix,item in enumerate(final_IDs):
            new_item = item.split()
            condition_ok = True
            for entity in new_item:
                if entity.isalpha():
                    condition_ok = False
            if condition_ok:
                finalised_IDs.append(item)

# start calling functions #
                
    all_texts, country_of_birth, genders = removefixedwords(final_all_get_text) #all pages compiled into one list    
    no_punc_text, final_all_texts = textpreprocessing1(all_texts)
    new_text = spacyNER(no_punc_text)
    xxx = textpreprocessing2(new_text)
    segregated_names,independent_names = nltkNER(xxx)
    joined_final_names, first_names, last_names = full_names(segregated_names, independent_names)
    for_validating = DOBs(__DOBs)
    IDs(all_possible_IDs)

# end calling functions #
   
    # =============================================================================
    #     #GET FIRST 6 DIGITS AS DOB IF MALAYSIA ID
    # 
    #     #if it is a 12-digit id and language is indonesian, it is a malaysia id
    #     
    #     condition_indonesia = False
    # 
    #     for ix,item in enumerate(lists[3]):
    #         dictionaryy=lists[3][ix]
    #         get_text=dictionaryy.get('Text')
    #         
    #         if get_text != None:
    #             doc = nlp(get_text)
    #             for i, sent in enumerate(doc.sents):
    #                 #print (sent._.language.get('language')) #retrieves iso language code
    #                 detected_language = sent._.language.get('language')
    #                 if detected_language != 'en':
    #                     classified_language = detected_language #non-en language
    #                     #print ('Language Identified:', classified_language) #malaysia and brunei will be classified as indonesia
    # 
    # #able to detect (ISO country codes):
    # #af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
    # #hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
    # #pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
    #  
    # #ISO directory: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    #                     
    #                     if detected_language == 'id':
    #                         condition_indonesia = True
    #     
    #     for item in finalised_IDs:
    #         if len(item) == 12 and condition_indonesia:
    #             malaysian_dob = item[0:6]
    #             finalised_IDs.append(malaysian_dob)
    #             #print ('NON-SINGAPORE: MALAYSIA') #top three most common country #good to look into it and uncomment if possible
    #             print ('Malaysia DOB is', malaysian_dob) #add malaysia DOBs to final output if any
    #         #if condition_isBrunei and condition_indonesia: 
    #             #print ('NON-SINGAPORE: BRUNEI') #top three most common country #good to look into it and uncomment if possible
    #         #else:
    #             #print ('NON-SINGAPORE: INDONESIA') #top three most common country #good to look into it and uncomment if possible
    # 
    # =============================================================================
    
    #######################################################################################################
    
    # =============================================================================
    # # (may want to comment autofit section out)
    #     
    #     # Autofit cell widths
    #     
    #     if final_full_names and first_names and last_names and final_DOBs and final_IDs:
    #         app = xw.App()
    #         wb = xw.Book(xlsx_filename)
    #         ws1 = wb.sheets['Sheet1']
    #         ws1.autofit()
    #         wb.save()
    #         app.quit()
    # =============================================================================
    
# =============================================================================
#     #to check output of first part of code
#     
#     txt_filename = '.\\Details at a Glance (' + dateStr + time + ').txt'
#     text_file_2 = open(txt_filename, "w")
# #    text_file_2.write("%s" % str(final_all_texts))
# #    text_file_2.write("\n")
# #    text_file_2.write("%s" % str(fulls_segregated_names))
# #    text_file_2.write("\n")
#     text_file_2.write("%s" % str(joined_final_names))
#     text_file_2.write("\n")    
#     text_file_2.write("%s" % str(first_names))
#     text_file_2.write("\n")
#     text_file_2.write("%s" % str(last_names))
#     text_file_2.write("\n")
#     text_file_2.write("%s" % str(final_DOBs))
#     text_file_2.write("\n")
#     text_file_2.write("%s" % str(finalised_IDs))
#     text_file_2.write("\n")
#     
#     text_file_2.close()
# =============================================================================

# =============================================================================
# ##### 13: ASL and ID files are distinguished using rule-based logics #####
#     
#     #CLASSIFY AS ASL OR ID
#     
#     conditioner1 = False
#     conditioner2 = False
#     conditioner3 = True
#     conditioner4 = True
#     
#     if len(final_DOBs) == 0 or len(finalised_IDs) == 0:
#         conditioner1 = True
#         
#     if len(final_DOBs) == 0 and len(finalised_IDs) == 0:
#         conditioner2 = True
#     
#     if conditioner1 and conditioner2: #ASLs have at least one of either DOBs or IDs completely missing
#         print ('CLASSIFY AS ASL')
#         conditioner3 = False
#         conditioner4 = False
#     
#     if len(new_all_matching) < 21 and conditioner3: #IDs have less than 21 recognised 'final full name' entities
#         print ('CLASSIFY AS ID')
#         conditioner4 = False
#     
#     if conditioner4: #everything else
#         print ('CLASSIFY AS ASL')
# =============================================================================
        
    #######################################################################################################
    
    df1 = pd.DataFrame({'Full Name': joined_final_names})
    df2 = pd.DataFrame({'First Name': first_names})
    df3 = pd.DataFrame({'Last Name': last_names})
    df4 = pd.DataFrame({'Date of Birth': final_DOBs})
    df5 = pd.DataFrame({'ID': finalised_IDs})
    df6 = pd.DataFrame({'Place of Birth': country_of_birth})
    df7 = pd.DataFrame({'Gender': genders})
        
    xlsx_filename = '.\\Final Client Details (' + dateStr + time + ').xlsx'
    
    writer = pd.ExcelWriter(xlsx_filename, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    df1.to_excel(writer, sheet_name='Sheet1', startcol=0, index = False)
    df2.to_excel(writer, sheet_name='Sheet1', startcol=1, index = False)
    df3.to_excel(writer, sheet_name='Sheet1', startcol=2, index = False)
    df4.to_excel(writer, sheet_name='Sheet1', startcol=3, index = False)
    df5.to_excel(writer, sheet_name='Sheet1', startcol=4, index = False)
    df6.to_excel(writer, sheet_name='Sheet1', startcol=5, index = False)
    df7.to_excel(writer, sheet_name='Sheet1', startcol=6, index = False)
    
    writer.save()    
    
    return xlsx_filename
