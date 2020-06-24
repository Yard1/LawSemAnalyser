# coding: UTF-8
import tempfile
import os
import io
import sys
import pprint
from xml.etree import ElementTree as ET
from io import StringIO, BytesIO
import collections
import string
import regex as re
from subprocess import Popen
import chardet
from bs4 import BeautifulSoup, NavigableString, UnicodeDammit
import codecs

import regex as re
import codecs
import os
from pprint import pprint
from typing import Generator
from enum import Enum, auto
from pathlib import Path

import json
import subprocess
from tqdm import tqdm
import docker


class HTMLExtractor(object):
    PATTERN_CLEAN_HMTL = re.compile(r"<.*?>")
    PATTERN_WHITESPACE = re.compile(r"(\s|\r|\n)+")
    PATTERN_HREF_REFERENCE = re.compile(r"<a\s+href\s*=\s*\"#([^\"]+?)\".*?<\/a>")

    PATTERN_EU_DOC = re.compile(r"href\s*=\s*\".*?eur-lex\.europa\.eu")

    TEMPLATES = ["title", "chapter", "subchapter", "article", "ref"]

    BAD_CHARS_TO_REPLACE = {
        "\u00ab": '"',  # left-pointing double angle quotation mark
        "\u00ad": "\-",  # soft hyphen
        "\u00b4": "'",  # acute accent
        "\u00bb": '"',  # right-pointing double angle quotation mark
        "\u00f7": "\/",  # division sign
        "\u01c0": "\|",  # latin letter dental click
        "\u01c3": "\!",  # latin letter retroflex click
        "\u02b9": "'",  # modifier letter prime
        "\u02ba": '"',  # modifier letter double prime
        "\u02bc": "'",  # modifier letter apostrophe
        "\u02c4": "\^",  # modifier letter up arrowhead
        "\u02c6": "\^",  # modifier letter circumflex accent
        "\u02c8": "'",  # modifier letter vertical line
        "\u02cb": "\`",  # modifier letter grave accent
        "\u02cd": "\_",  # modifier letter low macron
        "\u02dc": "\~",  # small tilde
        "\u0300": "\`",  # combining grave accent
        "\u0301": "'",  # combining acute accent
        "\u0302": "\^",  # combining circumflex accent
        "\u0303": "\~",  # combining tilde
        "\u030b": '"',  # combining double acute accent
        "\u030e": '"',  # combining double vertical line above
        "\u0331": "\_",  # combining macron below
        "\u0332": "\_",  # combining low line
        "\u0338": "\/",  # combining long solidus overlay
        "\u0589": "\:",  # armenian full stop
        "\u05c0": "\|",  # hebrew punctuation paseq
        "\u05c3": "\:",  # hebrew punctuation sof pasuq
        "\u066a": "\%",  # arabic percent sign
        "\u066d": "\*",  # arabic five pointed star
        "\u200b": "",  # zero width space
        "\u2010": "\-",  # hyphen
        "\u2011": "\-",  # non-breaking hyphen
        "\u2012": "\-",  # figure dash
        "\u2013": "\-",  # en dash
        "\u2014": "\-",  # em dash
        "\u2015": "\-\-",  # horizontal bar
        "\u2016": "\|\|",  # double vertical line
        "\u2017": "\_",  # double low line
        "\u2018": "'",  # left single quotation mark
        "\u2019": "'",  # right single quotation mark
        "\u201a": "\,",  # single low-9 quotation mark
        "\u201b": "'",  # single high-reversed-9 quotation mark
        "\u201c": '"',  # left double quotation mark
        "\u201d": '"',  # right double quotation mark
        "\u201e": '"',  # double low-9 quotation mark
        "\u201f": '"',  # double high-reversed-9 quotation mark
        "\u2032": "'",  # prime
        "\u2033": '"',  # double prime
        "\u2034": "'''",  # triple prime
        "\u2035": "\`",  # reversed prime
        "\u2036": '"',  # reversed double prime
        "\u2037": "'''",  # reversed triple prime
        "\u2038": "\^",  # caret
        "\u2039": "\<",  # single left-pointing angle quotation mark
        "\u203a": "\>",  # single right-pointing angle quotation mark
        "\u203d": "\?",  # interrobang
        "\u2044": "\/",  # fraction slash
        "\u204e": "\*",  # low asterisk
        "\u2052": "\%",  # commercial minus sign
        "\u2053": "\~",  # swung dash
        "\u2060": "",  # word joiner
        "\u20e5": "\\",  # combining reverse solidus overlay
        "\u2212": "\-",  # minus sign
        "\u2215": "\/",  # division slash
        "\u2216": "\\",  # set minus
        "\u2217": "\*",  # asterisk operator
        "\u2223": "\|",  # divides
        "\u2236": "\:",  # ratio
        "\u223c": "\~",  # tilde operator
        "\u2264": "\<\=",  # less-than or equal to
        "\u2265": "\>\=",  # greater-than or equal to
        "\u2266": "\<\=",  # less-than over equal to
        "\u2267": "\>\=",  # greater-than over equal to
        "\u2303": "\^",  # up arrowhead
        "\u2329": "\<",  # left-pointing angle bracket
        "\u232a": "\>",  # right-pointing angle bracket
        "\u266f": "\#",  # music sharp sign
        "\u2731": "\*",  # heavy asterisk
        "\u2758": "\|",  # light vertical bar
        "\u2762": "\!",  # heavy exclamation mark ornament
        "\u27e6": "\[",  # mathematical left white square bracket
        "\u27e8": "\<",  # mathematical left angle bracket
        "\u27e9": "\>",  # mathematical right angle bracket
        "\u2983": "\{",  # left white curly bracket
        "\u2984": "\}",  # right white curly bracket
        "\u3003": '"',  # ditto mark
        "\u3008": "\<",  # left angle bracket
        "\u3009": "\>",  # right angle bracket
        "\u301b": "\]",  # right white square bracket
        "\u301c": "\~",  # wave dash
        "\u301d": '"',  # reversed double prime quotation mark
        "\u301e": '"',  # double prime quotation mark
        "\ufeff": "",  # zero width no-break space
    }

    def __init__(self):
        return

    class LawDoc:
        def __init__(self, soup: BeautifulSoup, extractor):
            self.soup = soup
            self.extractor = extractor
            self.result = {
                "type": self.type,
                "document": {"elements": [], "references": []},
            }
            self._extract()

        def _extract(self):
            return None

    class PolishLawDoc(LawDoc):
        PATTERN = r"Dz\.\s*U\..*?$"
        PATTERN_YEAR = r"(z ([0-9]{4}) r\..*?)(?=z [0-9]{4} r\.|$)"
        PATTERN_NR_GROUP = r"Nr [0-9]+.*?(?=Nr|$|z [0-9]{4} r)"
        PATTERN_NR = r"Nr ([0-9]+)"
        PATTERN_POZ = r"(?<![\S\[])([0-9]+)"
        PATTERN_RE = re.compile(
            PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE
        )

        class LawEntry:
            def __init__(self, year, pos, no=None):
                self.year = year
                self.pos = pos
                self.no = no

            def __str__(self) -> str:
                return "Dz. U. z %s r.%s poz. %s" % (
                    self.year,
                    " Nr %s" % self.no if self.no else "",
                    self.pos,
                )

        def __init__(self, soup: BeautifulSoup, extractor):
            self.type = "Polish"
            super().__init__(soup, extractor)

        def _extract(self):
            current_element = []
            current_name = ""
            refs_flag = False
            title_done = False
            in_body = False
            last_child = None
            references_temp = []
            references = self.result["document"]["references"]
            elements = self.result["document"]["elements"]
            template_counters = dict((k, 1) for k in self.extractor.TEMPLATES)
            for child in self.soup.recursiveChildGenerator():
                just_text = self.extractor._clean_html(child)
                if not isinstance(child, NavigableString) and child.name == "body":
                    in_body = True
                attrs = getattr(child, "attrs", None)
                if attrs:
                    if "href" in attrs:
                        references_temp.append(attrs["href"][1:])
                    if (
                        child.name == "div"
                        and "id" in attrs
                        and "_%s" % attrs["id"] in references_temp
                    ):
                        refs_flag = True
                        element = {
                            "type": "ref",
                            "id": attrs["id"],
                            "content": just_text,
                            "links": [],
                        }
                        references.append(element)
                    elif not refs_flag and child.name == "a" and "href" in attrs:
                        ref = re.search(
                            r"<a\s+href\s*=\s*\"#([^\"]+?)\".*?<\/a>",
                            str(child),
                            re.DOTALL | re.IGNORECASE,
                        )
                        if ref:
                            ref_string = "_REF%s" % ref.group(1)
                            child.string = ref_string
                elif in_body and not refs_flag and isinstance(child, NavigableString):
                    if not title_done and re.match(r"Ustawa", just_text, re.IGNORECASE):
                        current_name = "title"
                        current_element = []
                        element = {
                            "type": current_name,
                            "id": 0,
                            "content": current_element,
                            "refs": [],
                        }
                        elements.append(element)
                        title_done = True
                    elif re.match(
                        r"(Rozdział [0-9]+)|(Dział [0-9]+)", just_text, re.IGNORECASE
                    ):
                        current_name = "chapter"
                        current_element = []
                        element = {
                            "type": current_name,
                            "id": template_counters[current_name],
                            "content": current_element,
                            "refs": [],
                        }
                        elements.append(element)
                        template_counters[current_name] += 1
                    elif re.match(
                        r"(Art\. [0-9]+\..*)|(Artykuł [0-9]+\..*)",
                        just_text,
                        re.IGNORECASE,
                    ):
                        current_name = "article"
                        current_element = []
                        element = {
                            "type": current_name,
                            "id": template_counters[current_name],
                            "content": current_element,
                            "refs": [],
                        }
                        elements.append(element)
                        template_counters[current_name] += 1
                    current_element.append(just_text)
            for element in elements:
                element["content"] = " ".join(
                    [x for x in element["content"] if x != ""]
                )
                for x in re.findall(r"_REF_(\w+)\b", element["content"]):
                    element["refs"].append(str(x))
            self._get_link_refs()

        def _get_link_refs(self):
            for reference in self.result["document"]["references"]:
                reference["links"] = [
                    "http://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU%s%s%s"
                    % (x.year, "000" if not x.no else x.no.zfill(3), x.pos.zfill(4))
                    for x in self._get_references(reference["content"])
                ]

        def _get_references(self, text: str) -> Generator:
            for item in self.PATTERN_RE.findall(text):
                years = re.findall(self.PATTERN_YEAR, item, overlapped=True)
                for year in years:
                    nrs = re.findall(self.PATTERN_NR_GROUP, year[0], overlapped=True)
                    if len(nrs) > 0:
                        for n in nrs:
                            nr = re.search(self.PATTERN_NR, n)
                            if nr:
                                poz_str = n.split("poz. ")
                                pozs = []
                                for p in poz_str[1:]:
                                    pozs.extend(re.findall(self.PATTERN_POZ, p))
                                for p in pozs:
                                    law = self.LawEntry(year[1], p, nr.group(1))
                                    yield law
                    else:
                        poz_str = year[0].split("poz. ")
                        pozs = []
                        for p in poz_str[1:]:
                            pozs.extend(re.findall(self.PATTERN_POZ, p))
                    for p in pozs:
                        law = self.LawEntry(year[1], p)
                        yield law

    class EULawDoc(LawDoc):
        def __init__(self, soup: BeautifulSoup, extractor):
            self.type = "EU"
            super().__init__(soup, extractor)

        def _extract(self):
            current_element = []
            current_name = ""
            refs_flag = False
            title_done = False
            in_body = False
            last_child = None
            references_temp = []
            references = self.result["document"]["references"]
            elements = self.result["document"]["elements"]
            last_chapter = None
            template_counters = dict((k, 1) for k in self.extractor.TEMPLATES)
            soup = self.soup.find("div", {"id": "docHtml"})
            soup = soup.find("div")
            for child in self.soup.recursiveChildGenerator():
                just_text = self.extractor._clean_html(child)
                attrs = getattr(child, "attrs", None)
                if child.parent == soup or (
                    child.parent.parent == soup and child.parent.name == "div"
                ):
                    if attrs and "class" in attrs:
                        if "doc-ti" in attrs["class"] and not current_name == "title":
                            current_name = "title"
                            element = {
                                "type": current_name,
                                "id": 0,
                                "content": current_element,
                                "refs": [],
                            }
                            elements.append(element)
                        elif (
                            not title_done
                            and "normal" in attrs["class"]
                            and not current_name == "INTRODUCTION"
                        ):
                            current_name = "introduction"
                            element = {
                                "type": current_name,
                                "id": 0,
                                "content": current_element,
                                "refs": [],
                            }
                            elements.append(element)
                            title_done = True
                        elif "ti-section-1" in attrs["class"]:
                            current_element = []
                            if re.match(r"TYTUŁ .*", just_text, re.IGNORECASE):
                                current_name = "chapter"
                                element = {
                                    "type": current_name,
                                    "id": template_counters[current_name],
                                    "content": current_element,
                                    "refs": [],
                                    "subelements": [],
                                }
                                last_chapter = element
                                elements.append(element)
                            else:
                                current_name = "subchapter"
                                if last_chapter["subelements"]:
                                    current_id = (
                                        last_chapter["subelements"][-1]["id"] + 1
                                    )
                                else:
                                    current_id = 1
                                element = {
                                    "type": current_name,
                                    "id": current_id,
                                    "content": current_element,
                                    "refs": [],
                                }
                                last_chapter["subelements"].append(element)
                            template_counters[current_name] += 1
                        elif "ti-art" in attrs["class"]:
                            current_name = "article"
                            current_element = []
                            element = {
                                "type": current_name,
                                "id": template_counters[current_name],
                                "content": current_element,
                                "refs": [],
                            }
                            elements.append(element)
                            template_counters[current_name] += 1
                        elif child.name == "p" and "note" in attrs["class"]:
                            current_name = "ref"
                            current_element = []
                            element = {
                                "type": current_name,
                                "id": template_counters[current_name],
                                "content": current_element,
                                "links": [],
                            }
                            references.append(element)
                            template_counters[current_name] += 1
                    current_element.append(child)
                    if current_name == "ref" and not isinstance(child, NavigableString):
                        current_element = []
                        references[-1]["links"].append(current_element)
                        links = [
                            getattr(x, "attrs", None)["href"]
                            for x in child.find_all("a")
                        ][-1:]
                        if len(links) > 0:
                            current_element.extend(links)
                if (
                    not current_name == "ref"
                    and attrs
                    and child.name == "span"
                    and "class" in attrs
                    and "note-tag" in attrs["class"]
                ):
                    if not "*" in child.string:
                        child.string = "_REF_%s" % just_text
            for element in elements:
                element["content"] = " ".join(
                    [
                        x
                        for x in [
                            self.extractor._clean_html(y) for y in element["content"]
                        ]
                        if x
                    ]
                )
                for x in re.findall(r"_REF_(\w+)\b", element["content"]):
                    element["refs"].append(str(x))
                if "subelements" in element:
                    for subelement in element["subelements"]:
                        subelement["content"] = " ".join(
                            [
                                x
                                for x in [
                                    self.extractor._clean_html(y)
                                    for y in subelement["content"]
                                ]
                                if x
                            ]
                        )
                        for x in re.findall(r"_REF_(\w+)\b", subelement["content"]):
                            subelement["refs"].append(str(x))
            for reference in references:
                reference["content"] = " ".join(
                    [
                        x
                        for x in [
                            self.extractor._clean_html(y) for y in reference["content"]
                        ]
                        if x
                    ]
                )
                reference["links"] = [str(x) for x in reference["links"][0] if x]

    def _replace_bad_chars(self, text: str) -> str:
        for k, v in self.BAD_CHARS_TO_REPLACE.items():
            text = text.replace(k, v)
        return text

    def _get_law_doc(self, soup: BeautifulSoup) -> LawDoc:
        if self.PATTERN_EU_DOC.search(str(soup)):
            law_doc = self.EULawDoc(soup, self)
        else:
            law_doc = self.PolishLawDoc(soup, self)
        return law_doc

    def extract_html(self, soup: BeautifulSoup) -> LawDoc:
        law_doc = self._get_law_doc(soup)
        return law_doc

    def _clean_html(self, html_string: str) -> str:
        return self._replace_bad_chars(
            re.sub(
                self.PATTERN_WHITESPACE,
                " ",
                re.sub(
                    self.PATTERN_CLEAN_HMTL, "", re.sub("&nbsp;", " ", str(html_string))
                ),
            ).strip()
        )

