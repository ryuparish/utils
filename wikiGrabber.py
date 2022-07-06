import argparse
import urllib.request
import requests
import time
import json, fileinput
from bs4 import BeautifulSoup as bsoup

parser = argparse.ArgumentParser(epilog="NOTE: Use the tsv file with the second column named as \"title\","
                                "same as what's downloaded from https://petscan.wmflabs.org/ after query search\n")
parser.add_argument('--tsv', action='store', type=str, help="load a tsv file")
parser.add_argument('--text', action='store', type=str, help="text file with urls on each line")
parser.add_argument('--level', action='store', default=2, type=int, help="the number of levels in the content outline")
parser.add_argument('--out', action='store', type=str, help="the output file path")
args = parser.parse_args()

if not (args.tsv or args.text):
    parser.error('No file type given at least one is needed, add --tsv or --text then filename')

if not args.out:
    parser.error('No output file given, add --out then filename')


def _too_short_article(article):
    length = len(article.split())
    # print(f"article length: {length}")
    return length < 3000

def _too_short_first_paragraph(firstParagraph):
    length = len(firstParagraph.split())
    # print(f"first paragraph length: {length}")
    return length < 30

def _too_small_content_outline(contentOutline):
    length = len(contentOutline.split("\n"))
    # print(f"content outline length: {length}")
    return length < 30

def _invalid_title(title):
    if title.replace("_", " ").split()[0].lower() in ["list", "lists"]: # we can add more citeria
        return True
    return False

def _too_few_outgoing_links(outgoing_links):
    # print(f"# outgoing links: {outgoing_links}")
    return outgoing_links < 200

def _too_frequent_changes(nChanges):
    # print(f"# edits since 2022/03/01: {nChanges}")
    return nChanges > 15

def exclude_redundant_sections(contentOutline, sectionName):
    if f'<a href="#{sectionName}"' in contentOutline:
        contentOutline = '<li'.join(str(contentOutline).split(f'<a href="#{sectionName}"')[0].split('<li')[:-1])
    return contentOutline

def get_num_recent_changes(titles):
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": titles,
        "rvprop": "timestamp|comment",
        "rvslots": "main",
        "rvend": "2022-03-01T00:00:00Z",
        "rvdir": "older",
        "format": "json",
        "rvlimit": 30
    }
    response = requests.get("https://en.wikipedia.org/w/api.php", params=params)
    values = list(response.json()['query']['pages'].values())
    nChanges_list = []
    for pageInfo in values:
        if "revisions" not in pageInfo:
            nChanges_list += [0]
        else:
            nChanges_list += [len(pageInfo["revisions"])]
    return nChanges_list

def get_outgoing_links(titles):
    params = {'format':'json', 'action':'query', 'plnamespace': '0', 'pllimit': 210, 'prop':'links', 'titles':titles}
    response = requests.get("https://en.wikipedia.org/w/api.php", params=params)
    values = list(response.json()['query']['pages'].values())
    nLinks_list = []
    for pageInfo in values:
        if "links" not in pageInfo:
            nLinks_list += [0]
        else:
            nLinks_list += [len(pageInfo["links"])]
    return nLinks_list

def get_page_html(urls, titles):

    # Send request to wikipedia for only the first paragraph in wikipedia page
    params = {'format':'json', 'action':'query', 'explaintext':'true','prop':'extracts', 'titles':titles}
    response = requests.get("https://en.wikipedia.org/w/api.php", params=params)
    values = list(response.json()['query']['pages'].values())

    full_articles = []
    contentOutlines = []
    for i in range(len(urls)):
         # Get and parse html from url
        html = urllib.request.urlopen(urls[i])
        parsedHtml = bsoup(html, 'html.parser')
        full_article = values[i]['extract']

        contentOutline = parsedHtml.find('div', {"id": "toc"})

        # Cleaning all tags in the toc that are greater than the given argument for level
        if args.level is not None:
            givenLevel = "toclevel-" + str(int(args.level)+1)
            for _, li_tag in enumerate(contentOutline.findAll('li', {"class": givenLevel})):
                li_tag.decompose()

        # Removing the see also and afterwards of the toc
        contentOutline = str(contentOutline)
        for sectionName in ["See_also", "Notes", "References", "External_links", "Further_reading", "Bibliography", "Footnotes"]:
            contentOutline = exclude_redundant_sections(contentOutline, sectionName)

        contentOutline = contentOutline + "\n </ul>\n</div>"
        full_articles += [full_article]
        contentOutlines += [contentOutline]
    return full_articles, contentOutlines


def getWikiInfo(start_idx, urls, utterances=None):

    # Finding the first paragraph that is isn't a special class and is under a div
    titles = [url.split("/")[-1].strip() for url in urls]
    titles_string = '|'.join(titles)

    print(f"titles: {titles_string}")

    
    try:
        nChanges_list = get_num_recent_changes(titles_string)
        nLinks_list = get_outgoing_links(titles_string)
        full_articles, contentOutlines = get_page_html(urls, titles_string)
    except:
        print("error found .. skip ..")
        return [None] * len(urls)


    sourceLines = []
    for i in range(len(urls)):
        if _too_frequent_changes(nChanges_list[i]) or _too_few_outgoing_links(nLinks_list[i]) or _invalid_title(titles[i]):
        # if _too_few_outgoing_links(nLinks[i]) or _invalid_title(titles[i]):
            sourceLines += [None]
            continue

        firstParagraph = full_articles[i].split("\n")[0]
        if _too_short_first_paragraph(firstParagraph) or _too_short_article(full_articles[i]) or _too_small_content_outline(contentOutlines[i]):
            sourceLines += [None]
            continue

        newData = {
            'utterances' : [],
            'prevEvidence' : [],  # For each previous agent utterance
            'annotations' : [],  # only need for validation
            'wikipedia' : {
                "article" : "",
                "outline" : "",
                "title" : ""
            }
        }
        # Add to json object
        if utterances:
            newData['utterances'] = utterances[i]

        newData['wikipedia']['article'] = firstParagraph
        newData['wikipedia']['outline'] = contentOutlines[i]
        newData['wikipedia']['title'] = titles[i]

        # Convert to JSON and then insert into sources.jsonl
        newData = json.dumps(newData)
        question_id = "dial_" + str(start_idx+i) + "_turn_1_user"
        sourceLine = {"id" : question_id, "question" : newData}
        sourceLines += [sourceLine]
    return sourceLines


def readTextFile():
    lines = open(args.text).readlines()[:10000]
    n_lines = 0
    start = time.time()
    interval = 1
    with open(args.out, mode='w') as dest:
        for idx in range(int(len(lines)/interval)+1):
            if idx*interval >= len(lines):
                continue
            urls = [line.strip() for line in lines[idx*interval:(idx+1)*interval]]
            sourceLines = getWikiInfo(idx*interval, urls)
            print(time.time()-start)
            for sourceLine in sourceLines:
                if sourceLine is None:
                    continue
                dest.write(json.dumps(sourceLine) + "\n")
                n_lines += 1
                if (n_lines%10) == 0:
                    print(n_lines, idx*interval, time.time()-start)


def readExcel():
    lines = [line for line in open(args.tsv).readlines()[:10000] if line.strip().lower()!="article" and line.strip()!=""]
    start = time.time()
    n_lines = 0
    interval = 1
    with open(args.out, mode='w') as dest:
        for idx in range(int(len(lines)/interval)+1):
            if idx*interval >= len(lines):
                continue
            urls = ['https://en.wikipedia.org/wiki/' + '_'.join(line.split('\t')[1].replace("*", "").strip().split()) for line in lines[idx*interval:(idx+1)*interval]]
            sourceLines = getWikiInfo(idx*interval, urls)
            for sourceLine in sourceLines:
                if sourceLine is None:
                    continue
                dest.write(json.dumps(sourceLine) + "\n")
                n_lines += 1
                if (n_lines%10) == 0:
                    print(n_lines, idx*interval, time.time()-start)


def main():
    if args.tsv:
        readExcel()
    else:
        readTextFile()

main()
