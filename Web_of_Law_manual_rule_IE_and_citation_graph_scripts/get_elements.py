__author__ = 'halley'

import os
import xml.etree.ElementTree as ET
import wol_utilities
from wol_utilities import almostEquals, standardize

def getDateElement(trees, xml_line, local_citations):
    attribs = xml_line.attrib

    relation_trees = list(filter(lambda i: i.tag == 'RELATION', trees))
    relation_trees = list(filter(lambda i: 'at_date' in i.attrib, relation_trees))
    for relation_tree in relation_trees:
        if relation_tree.attrib['at_date'] == attribs['id']:
            id = relation_tree.attrib['theme']
            for local_citation in local_citations:
                if local_citation['id'] == id:
                    attribs['citation_local_level_id'] = local_citation['citation_local_level_id']
                    attribs['citation_global_level_id'] = local_citation['citation_global_level_id']
                    break
            break
    return attribs

def getDocketElement(trees, xml_line, local_citations):
    attribs = xml_line.attrib
    text = xml_line.text

    relation_trees = list(filter(lambda i: i.tag == 'RELATION', trees))
    relation_trees = list(filter(lambda i: 'includes_docket_string' in i.attrib, relation_trees))
    for relation_tree in relation_trees:
        if relation_tree.attrib['includes_docket_string'] == text:
            id = relation_tree.attrib['theme']
            for local_citation in local_citations:
                if local_citation['id'] == id:
                    attribs['citation_local_level_id'] = local_citation['citation_local_level_id']
                    attribs['citation_global_level_id'] = local_citation['citation_global_level_id']
                    attribs['lookup_key'] = local_citation['lookup_key']
                    break
            break
    return attribs

def getName(xml, all_citations, local_names):
    attribs = xml.attrib
    text = xml.text
    standard = standardize(text)
    attribs['name'] = standard
    for id, names in local_names.items():
        for name in names:
            if almostEquals(standard, name):
                attribs['local_name_id'] = id
                break
    if 'local_name_id' not in attribs:
        attribs['local_name_id'] = max(local_names.keys()) + 1
    return attribs


#get the legal role of the current xml tree
def getLegalRoleElement(words, trees, current_tree, local_names):
    attribs = current_tree.attrib
    trees = filter(lambda i: i.tag == 'RELATION', trees) #get only relation trees
    trees = map(lambda i: i.attrib, trees)
    #look for a relation tree where the 'legal_role' has the same id as the current tree
    for tree in trees:
        if 'legal_role' in tree:
            if tree['legal_role'] == wol_utilities.standardize(attribs['id']):
                attribs['name'] = tree['theme_string']
                for id, names in local_names.items():
                    for name in names:
                        if wol_utilities.almostEquals(name, attribs['name']):
                            attribs['local_name_id'] = id
                if 'local_name_id' not in attribs:
                    attribs['local_name_id'] = max(local_names.keys()) + 1
                break
    text = current_tree.text.lower()
    if text in ['appellant', 'appellant\'s', 'appellant']:
        attribs['party'] = "party1"
    elif text in ['appellee', 'appellees', 'appellee\'s']:
        attribs['party'] = "party2"
    return attribs

#get xml attributes of a profession element
def getProfessionElement(trees, xml_line, local_names):
    attribs = xml_line.attrib

    relation_trees = filter(lambda i: i.tag == 'RELATION', trees)

    #search for a relation that has a profession_string equal to the profession of the xml_line
    for rtree in relation_trees:
        rattrib = rtree.attrib
        if 'profession_string' in rattrib:
            prof = rattrib['profession_string']
            profession_name = wol_utilities.standardize(rattrib['theme_string'])
            if prof == xml_line.text:
                attribs['party'] = profession_name
                for id, names in local_names.items():
                    for name in names:
                        if wol_utilities.almostEquals(profession_name, name):
                            attribs['document_level_name_id'] = id
                            break
                if 'document_level_name_id' not in attribs:
                    attribs['document_level_name_id'] = max(local_names.keys()) + 1
                break
    return attribs

