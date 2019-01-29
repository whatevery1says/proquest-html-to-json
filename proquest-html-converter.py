import re
import os
import glob
import json
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as dateparser

proquest_dir = '/Users/lxt308/testing/proquest-html/proquest-data/'
results_dir = '/Users/lxt308/testing/proquest-html/results-script/'

# Determine the filenames of the ProQuest html files that will be converted to individual json files.
datafile_list = []
for (dirname, _dirs, files) in os.walk(proquest_dir):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(dirname.split(proquest_dir)[1], filename)
            datafile_list.append(filepath)

# Chop up single html file into individual files according to a set delimiter. We aren't saving these individual html files.
# Then, a monstrous for loop to strip info from each html file using combo of Beautiful soup and regex and put into dict. ProQuest html files are very poorly tagged.
# Dump dict into json files in json directory. Save each json file with a padded id as the filename in a subdirectory determined by the original ProQuest file it came from (so, all individual articles from the same original ProQuest results html file will be in the same subdirectory). 
html_split = []
article = {}
for file in datafile_list:
    file_name = os.path.splitext(os.path.basename(file))[0]
    sub_dir = results_dir + file_name
    if not os.path.isdir(sub_dir):
        os.makedirs(sub_dir)
    filepath_html = proquest_dir + file
    with open(filepath_html, 'rt') as infile:
       html_file = infile.read()
    html_split = html_file.split('<div style="margin-bottom:20px;border-bottom:2px solid #ccc;padding-bottom:5px">')
    idx = 0
    for html in html_split:
        padded_id = str(idx).zfill(len(str(len(html_split))))
        article_path = proquest_dir + html
        soup = BeautifulSoup(html, 'html.parser')
        p_tags = soup.find_all('p')
        everything = str(soup)
        body_tags = soup.find_all('body')
        # article title
        try:
            just_second = p_tags[1]
            article_title = just_second.get_text()
            article['title'] = article_title
        except Exception as exc:
            print('! error finding article_title')
            article['title'] = ''
        # doc-id
        try:
            doc_id = str(soup.find('a'))
            doc_id = re.sub('<a name="', '', doc_id)
            doc_id = re.sub('"></a>', '', doc_id)
            article['doc_id'] = doc_id
        except Exception as exc:
            print('! error finding doc-id')
            article['doc_id'] = ''
        # pub
        try:
            pub_title_obj = re.search('<strong>Publication title: </strong>(.+?)</p>', everything)
            pub_title = pub_title_obj.group(1)
            article['pub'] = pub_title
        except Exception as exc:
            print('! error finding pub_title')
            article['pub'] = ''
        # pub-date
        bad_date = '1900-01-01T00:00:00Z'
        try:
            pub_date_obj = re.search('<strong>Publication date: </strong>(.+?)</p>', everything)
            if pub_date_obj:
                pub_date = pub_date_obj.group(1)
            pub_date = re.sub('([a-zA-Z]*)\/([a-zA-Z]*)', r'\1', pub_date)
            date=''
            parse_date = pub_date
            while not date:
                try:
                    date = dateparser.parse(parse_date)
                except Exception as exc:
                    print(' ! error parsing pub_date', exc)
                    parse_date = ' '.join(parse_date.split(' ')[:-1])
                if not parse_date or parse_date.isspace():
                    break
            date_out = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception as exc:
            print('! error finding pub-date')
            date_out = bad_date
        # volume
        try:
            volume_obj = re.search('<strong>Volume: </strong>(.+?)</p>', everything)
            volume = volume_obj.group(1)
            article['volume'] = volume
        except Exception as exc:
            print('! error finding volume')
            article['volume'] = ''
        # issue
        try:
            issue_obj = re.search('<strong>Issue: </strong>(.+?)</p>', everything)
            issue = issue_obj.group(1)
            article['issue'] = issue
        except Exception as exc:
            print('! error finding issue')
            article['issue'] = ''
        # content
        try:
            just_second_body = body_tags[1]
            article_text = just_second_body.get_text()
            article['content'] = article_text
        except Exception as exc:
            print('! error finding article content')
            article['content'] = ''
        # length
        try:
            length = len(article_text)
            article['length'] = length
        except Exception as exc:
            print('! error finding length')
        # section
        try:
            section_obj = re.search('<strong>Section: </strong>(.+?)</p>', everything)
            section = section_obj.group(1)
            article['section'] = section
        except Exception as exc:
            print('! error finding section')
            article['section'] = ''
        # author
        try:
            just_author = p_tags[2]
            author = just_author.get_text()
            author = re.sub('Author: ', '', author)
            article['author'] = author
        except Exception as exc:
            print('! error finding author')
            article['author'] = ''
        # copyright
        try:
            pub_info_obj = re.search('<strong>Publication info: </strong>(.+?)</p>', everything)
            pub_info = pub_info_obj.group(1)
            article['copyright'] = pub_info
        except Exception as exc:
            print('! error finding copyright')
            article['copyright'] = ''
        # database
        try:
            database_obj = re.search('<strong>Database: </strong>(.+?)</p>', everything)
            database = database_obj.group(1)
            article['database'] = database
        except Exception as exc:
            print('! error finding database')
            article['database'] = 'ProQuest'
        #name
        try:
            pub_title_transform = ''.join(pub_title.split())
            pub_title_transform = re.sub(r'[^\w]','',pub_title_transform)
            name = pub_title_transform + '_' + file_name
        except Exception as exc:
            print('! error adding name')
            article['name'] = ''
        try:
            article['attachment-id'] = ''
            article['name'] = name 
            article['namespace'] = "we1sv2.0"
            article['metapath'] = "Corpus," + name + ",RawData"
            article['pub_date'] = date_out
            article['raw_date'] = pub_date
        except Exception as exc:
            print('! error adding extra keys')
        with open(sub_dir + '/' + file_name + '_' + padded_id + '_.json', 'w') as outfile:
            json.dump(article, outfile, sort_keys=True, indent=2)           
        idx = idx+1  

# Delete the first json file in each subdirectory, since it is a list of links.
for path, subdirs, files in os.walk(results_dir, topdown=True):
    for name in files:
        if '_00_.json' in name:
            first_file = os.path.join(path, name)
            os.remove(first_file)

# Zip up each subdirectory and delete unzipped directory
for path, subdirs, files in os.walk(results_dir, topdown=True):
    for subdir in subdirs:
       single_subdir = os.path.join(path, subdir)
       shutil.make_archive(single_subdir,'zip',single_subdir)
       shutil.rmtree(single_subdir)
