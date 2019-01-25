import re
import os
import glob
import json
import zipfile
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as dateparser

# still need to figure out how to make it print keys even if it doesn't find any info
filepath_html = 'proquest-html-1-10.html'
html_dir = '/Users/lxt308/testing/proquest-html/results/'
list_html_dir = os.listdir(html_dir)
json_dir = '/Users/lxt308/testing/proquest-html/json/'
file = 'ProQuestDocuments_Gender_EthnicNewsWatch_humanities_2017-01-01_2017-12-31.html'
article = {}


for item_idx, item in enumerate(list_html_dir):
    article_path = html_dir + item
    with open(article_path, 'r', errors='ignore') as infile:
        html_file = infile.read()
    soup = BeautifulSoup(html_file, 'html.parser')
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
        pub_title_obj = re.search('<strong>Publication title: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Volume: ', everything)
        pub_title_text = pub_title_obj.group(0)
        pub_title = re.sub('<strong>Publication title: </strong>', '', pub_title_text)
        pub_title = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Volume:', '', pub_title)
        article['pub'] = pub_title
    except Exception as exc:
        print('! error finding pub_title')
        article['pub'] = ''
    # pub-date
    bad_date = '1900-01-01T00:00:00Z'
    try:
        pub_date_obj = re.search('<strong>Publication date: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Section:', everything)
        if not pub_date_obj:
            pub_date_obj = re.search('<strong>Publication date: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Publisher:', everything)
            pub_date_text = pub_date_obj.group(0)
            pub_date = re.sub('<strong>Publication date: </strong>', '', pub_date_text)
            pub_date = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Publisher:', '', pub_date)
        pub_date_text = pub_date_obj.group(0)
        pub_date = re.sub('<strong>Publication date: </strong>', '', pub_date_text)
        pub_date = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Section:', '', pub_date)
        date=''
        parse_date = pub_date
        while not date:
            try:
                date = dateparser.parse(parse_date)
             #   print(' parsed: ', date)
            except Exception as exc:
                print(' ! error parsing pub_date', exc)
                parse_date = ' '.join(parse_date.split(' ')[:-1])
            if not parse_date or parse_date.isspace():
                break
        date_out = date.strftime('%Y-%m-%dT%H:%M:%SZ')
      #  if not date_out:
         # date_out = bad_date
    except Exception as exc:
        print('! error finding pub-date')
        date_out = bad_date
    # volume
    try:
        volume_obj = re.search('<strong>Volume: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Issue:', everything)
        volume_text = volume_obj.group(0)
        volume = re.sub('<strong>Volume: </strong>', '', volume_text)
        volume = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Issue:', '', volume)
        article['volume'] = volume
    except Exception as exc:
        print('! error finding volume')
        article['volume'] = ''
    # issue
    try:
        issue_obj = re.search('<strong>Issue: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Pages:', everything)
        issue_text = issue_obj.group(0)
        issue = re.sub('<strong>Issue: </strong>', '', issue_text)
        issue = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Pages:', '', issue)
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
        section_obj = re.search('<strong>Section: </strong>.+</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Publisher:', everything)
        section_text = section_obj.group(0)
        section = re.sub('<strong>Section: </strong>', '', section_text)
        section = re.sub('</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding-left:0;"><strong>Publisher:', '', section)
        article['section'] = section
    except Exception as exc:
        print('! error finding section')
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
        pub_info_obj = re.search('<strong>Publication info: </strong>.+.</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding:0;"><a href=', everything)
        pub_info_text = pub_info_obj.group(0)
        pub_info = re.sub('<strong>Publication info: </strong>', '', pub_info_text)
        pub_info = re.sub('.</p><p style="margin-bottom:5pt; margin-top:0; margin-right:0; margin-left:0; padding:0;"><a href=', '', pub_info)
        article['copyright'] = pub_info
    except Exception as exc:
        print('! error finding copyright')
        article['copyright'] = ''
    # database
    try:
        database_obj = re.search('<strong>Database: </strong>.+</p>', everything)
        database_text = database_obj.group(0)
        database = re.sub('<strong>Database: </strong>', '', database_text)
        database = re.sub('</p>', '', database)
        article['database'] = database
    except Exception as exc:
        print('! error finding database')
        article['database'] = 'ProQuest'
    #name
    try:
        name = pub_title + file
    except Exception as exc:
        print('! error adding name')
    try:
        article['attachment-id'] = ''
        article['name'] = name 
        article['namespace'] = "we1sv2.0"
        article['metapath'] = "Corpus," + name + ",RawData"
        article['pub_date'] = date_out
        article['raw_date'] = pub_date
    except Exception as exc:
        print('! error adding extra keys')
    with open(json_dir + item + '.json', 'w') as outfile:
        json.dump(article, outfile, sort_keys=True, indent=2)