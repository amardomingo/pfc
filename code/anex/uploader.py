#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse

import requests

from xml.dom import minidom
import json

solr_url="{url}/{core}/update"
solr_commit="<commit/>"
solr_clear="<delete><query>*:*</query></delete>"
solr_charset ='utf-8'

def get_tags():
    """
    Read the taglist file for the equivalences between rdf and json structure
    """
    flines = open('taglist.txt').readlines()
    eq = {}
    for line in flines:
        if line != '':
            line_data = line.split(',')
            eq[str(line_data[0])] = str(line_data[1].strip())
    print(eq)
    return eq



def commit(args):
    '''
    Commits the changes
    '''
    url = solr_url.format(url=args.url, core=args.core)
    headers = {'Content-type':'text/xml', 'charset':solr_charset}
    requests.post(url, data=solr_commit, headers=headers)


def clear(args):
    '''
    Clears the solr core
    '''
    url = solr_url.format(url=args.url, core=args.core)
    
    headers = {'Content-type':'text/xml', 'charset':solr_charset}
    
    requests.post(url, data=solr_clear, headers=headers)
    commit(args)

def read_xml(data_file):
    """
    Read the data from the xml file  
    """
    # Correspondence
    rdf2json = get_tags()

    xmlfile = minidom.parse(data_file)

    # Each element in this file, is an rdf:Description
    itemlist = xmlfile.getElementsByTagName('rdf:Description')
    
    documents = []
    for element in itemlist:
        doc = {}
        # First, read all this attributes
        for node in element.attributes.items():
            if node[0] in rdf2json:
                doc[rdf2json[node[0]]] = node[1]
        # Now, repeat for the children
         
        for childnode in element.childNodes:
            name = str(childnode.nodeName.strip())
            if name in rdf2json:
                value = ""
                # the value for rdf:type is sometimes stored as an attribute
                if len(childnode.attributes.items()) != 0:
                    value = childnode.attributes.items()[0][1]
                else:
                    value = childnode.firstChild.nodeValue
                doc[rdf2json[name]] = value

        # The doc is complete
        documents.append(doc)
    return documents

def read_json(data_file):
    '''
    Read the data from the provided json
    '''
    
    json_file = open(data_file, 'r')
    
    data = json.loads(json_file.read())
    
    return data

def upload_doc(doc, args):
    '''
    Upload a doc to solr
    '''
    url = solr_url.format(url=args.url, core=args.core)
    operations = {'add':{'doc':doc}} 
    
    headers = {'Content-type':'application/json', 'charset':solr_charset}
    
    requests.post('{url}/json'.format(url=url), data=json.dumps(operations), headers=headers)
    
def main(args):
    '''
    Perform the necessary requests
    '''
    # Clears the core, if asked
    if args.empty:
        clear(args)
        if args.verbose:
            print("Data in core {core} cleared".format(args.core), file=args.output)

    if args.verbose >2:
        print("Reading data from {file}".format(args.file), file=args.output)
    data = []
    if args.data:
        data += read_json(args.data)
    elif args.rdf:
        data += read_xml(args.rdf)
    else:
        print("Need at least an rdf or json file to read", file=sys.stderr)
        exit(1)
    
    # There is no actual numeric id, so...
    i = 1
    for doc in data:
        if 'id' not in doc:
            doc['id'] = i
        i+=1
        upload_doc(doc, args)
    commit(args)
        
    print("Uploaded all {number} doc to solr".format(number=str(len(data))), file=args.output)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Uploader for solr", add_help=True)
    parser.add_argument('-u', '--url', default="http://localhost:8080/solr", help="URL for the solr install")
    parser.add_argument('-c', '--core', default="gsidata", help="The core in use")
    parser.add_argument('-d', '--data', default="gsisemanticdata.json", help="A file with json data")
    parser.add_argument('-r', '--rdf', default=None, help="A file with rdf data")
    parser.add_argument('-v', '--verbose', action='count', help="Print debug info")
    parser.add_argument('-e', '--empty', action='store_true', help="Clear the data before upload")
    parser.add_argument('-o', '--output', default=sys.stdout, help="Log output file")
    parser.set_defaults(empty=False)
    args = parser.parse_args()
    # Get log output
    if args.output != sys.stdout:
        args.output = codecs.open(args.output, 'w+', 'utf-8-sig')
    main(args)
