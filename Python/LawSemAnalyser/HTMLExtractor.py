# coding: UTF-8
from typing import Generator
import regex as re
from bs4 import BeautifulSoup, NavigableString
from copy import copy
from collections import defaultdict


class HTMLExtractor(object):
    PATTERN_CLEAN_HMTL = re.compile(r"<.*?>")
    PATTERN_WHITESPACE = re.compile(r"(\s|\r|\n)+")

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
                "document": {"body": [], "glossary": []},
            }
            self.html_result = self.result.copy()
            self._extract()

        def _extract(self):
            return None

        def _create_element(
            self, type_str: str, id_str: str, content=None, links=None
        ) -> dict:
            return {
                "type": type_str,
                "id": id_str,
                "content": content if content else [],
                "links": links if links else [],
            }

        def _create_link(self, text: str, address: str, is_external: bool, is_generated: bool = False) -> dict:
            return {
                "text": text,
                "address": address,
                "is_external": is_external,
                "is_generated": is_generated,
            }

    class ISAPLawDoc(LawDoc):
        def __init__(self, soup: BeautifulSoup, extractor):
            self.type = "ISAP"
            super().__init__(soup, extractor)

        def _extract(self):
            glossary = self.result["document"]["glossary"]
            body = self.result["document"]["body"]
            soup = self.soup.find("body")

            section = soup.find("h1")
            title = []
            subtitle = []
            for child in section.children:
                title.append(child.contents[0])
                if len(child.contents) > 1:
                    subtitle.append(child.contents[1])
            body.append(self._create_element("title", "0", title))
            body.append(self._create_element("subtitle", "0", subtitle))

            sections = soup.find_all("section", id=re.compile(r"part_[0-9]+"))
            section = sections[0]
            block = section.find("div", "block")

            introduction = [
                section.find("h2", attrs={"class": "part"}),
                block.find("div", attrs={"class": "pro-text"}),
            ]
            body.append(self._create_element("introduction", "0", introduction))

            chapters = block.find_all(attrs={"class": "unit_chpt"}, recursive=False)
            for chapter in chapters:
                header = list(chapter.find_all("p", recursive=False))
                body.append(
                    self._create_element("chapter", chapter.attrs["data-id"], header)
                )
                div_inner = chapter.find("div")
                articles = div_inner.find_all(
                    lambda x: x.has_attr("class") and "unit_arti" in x["class"],
                    recursive=False,
                )
                for article in articles:
                    links = article.find_all("a")
                    body.append(
                        self._create_element(
                            "article", article.attrs["data-id"], [article]
                        )
                    )

            paragraphs = section.find("div", "block").find_all(
                attrs={"class": "unit_para"}, recursive=False
            )
            for paragraph in paragraphs:
                links = paragraph.find_all("a")
                body.append(
                    self._create_element(
                        "paragraph", paragraph.attrs["data-id"], [paragraph]
                    )
                )

            glossary_html = section.find("div", "gloss-section").find_all(
                "div", attrs={"class": "gloss"}, recursive=False
            )
            for gloss in glossary_html:
                glossary.append(
                    self._create_element("gloss", gloss.attrs["id"], gloss.contents)
                )

            appendices = sections[1:] if len(sections) > 1 else []

            for appendix in appendices:
                appendix = appendix.find("div", attrs={"class": "part"})
                body.append(
                    self._create_element("appendix", appendix.attrs["id"], [appendix])
                )

            for element in body + glossary:
                for child in element["content"]:
                    if isinstance(child, NavigableString):
                        continue
                    links = list(child.find_all("a"))
                    if child.name == "a":
                        links.append(child)
                    for link in links:
                        if not link.has_attr("href"):
                            continue
                        is_external = True
                        if link.attrs["href"][0] == "#":
                            is_external = False
                            address = link.attrs["href"][1:]
                        else:
                            address = link.attrs["href"]
                        element["links"].append(
                            self._create_link(
                                self.extractor._clean_html(link), address, is_external
                            )
                        )

            self.html_result["document"]["body"] = body.copy()
            self.html_result["document"]["glossary"] = glossary.copy()

            for element in body + glossary:
                element["content"] = " ".join(
                    [
                        x
                        for x in [
                            self.extractor._clean_html(y) for y in element["content"]
                        ]
                        if x
                    ]
                )

        def _create_link(self, text: str, address: str, is_external: bool, is_generated: bool = False) -> dict:
            if is_external and address.startswith("/api"):
                address = address.replace("/api", "http://isap.sejm.gov.pl/api", 1)
            return {
                "text": text,
                "address": address,
                "is_external": is_external,
                "is_generated": is_generated
            }

    class GenericPolishLawDoc(LawDoc):
        def __init__(self, soup: BeautifulSoup, extractor):
            self.type = "GenericPolish"
            super().__init__(soup, extractor)

        def _extract(self):
            glossary = self.result["document"]["glossary"]
            body = self.result["document"]["body"]
            soup = self.soup.find("body")

            if len(list(soup.find_all(recursive=False))) == 1:
                soup = soup.find("div")

            body_html = copy(soup)
            body_html.find_all(recursive=False)[-1].decompose()
            body_html = body_html.find_all("p", attrs={"class": True})

            def get_clean_text(tag):
                if not isinstance(tag, NavigableString):
                    tag = tag.get_text(" ", strip=True)
                return self.extractor._clean_html(tag)

            elements = []
            current_elements = []

            for tag in body_html:
                clean_tag = get_clean_text(tag)
                if clean_tag.lower() == "ustawa":
                    elements.append(["title", "0", []])
                    current_elements = elements[-1][-1]
                    elements.append(["subtitle", "0", []])
                else:
                    chapter_match = re.match(
                        r"Rozdział ([0-9]+)", clean_tag, re.IGNORECASE
                    )
                    article_match = re.match(
                        r"Art\. ([0-9]+)\.", clean_tag, re.IGNORECASE
                    )
                    appendix_match = re.match(
                        r"Załącznik nr ([0-9]+)", clean_tag, re.IGNORECASE
                    )
                    if chapter_match:
                        elements.append(["chapter", chapter_match.group(1), []])
                        current_elements = elements[-1][-1]
                    elif article_match:
                        elements.append(["article", article_match.group(1), []])
                        current_elements = elements[-1][-1]
                    elif appendix_match:
                        elements.append(["appendix", appendix_match.group(1), []])
                        current_elements = elements[-1][-1]
                if not re.match(r"Załączniki do ustawy z dnia.*", clean_tag):
                    current_elements.append(tag)

            def clean_content(content):
                return " ".join([get_clean_text(x) for x in content]).strip()

            body_html = [
                self._create_element(name, id, content)
                for name, id, content in elements
            ]

            glossary_html = soup.find_all(recursive=False)[-1].find_all(
                "div", attrs={"id": True}, recursive=False
            )
            glossary_html = [
                self._create_element("gloss", x.attrs["id"], x) for x in glossary_html
            ]

            for element in body_html + glossary_html:
                for child in element["content"]:
                    if isinstance(child, NavigableString):
                        continue
                    links = list(child.find_all("a"))
                    if child.name == "a":
                        links.append(child)
                    for link in links:
                        if not link.has_attr("href"):
                            continue
                        is_external = True
                        if link.attrs["href"][0] == "#":
                            is_external = False
                            address = link.attrs["href"][1:]
                            if address[0] == "_":
                                address = address[1:]
                        else:
                            address = link.attrs["href"]
                        if is_external or not element["type"] == "gloss":
                            element["links"].append(
                                self._create_link(
                                    self.extractor._clean_html(link),
                                    address,
                                    is_external,
                                )
                            )
                element["content"] = clean_content(element["content"])

            for element in glossary_html:
                for child in element["content"]:
                    for ref in self._get_references(child):
                        element["links"].append(
                            self._create_link(
                                ref.text,
                                "http://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU%s%s%s" % (ref.year, "000" if not ref.no else ref.no.zfill(3), ref.pos.zfill(4)),
                                True,
                                True
                            )
                        )

            self.html_result["document"]["body"] = body_html
            self.html_result["document"]["glossary"] = glossary_html

        def _create_link(self, text: str, address: str, is_external: bool, is_generated: bool = False) -> dict:
            if is_external and address.startswith("/api"):
                address = address.replace("/api", "http://isap.sejm.gov.pl/api", 1)
            return {
                "text": text,
                "address": address,
                "is_external": is_external,
                "is_generated": is_generated
            }

        class LawEntry():
            def __init__(self, text, year, pos, no = None):
                self.text = text
                self.year = year
                self.pos = pos
                self.no = no
            
            def __str__(self):
                return "Dz. U. z %s r.%s poz. %s" % (self.year, " Nr %s" % self.no if self.no else "", self.pos)


        def _get_references(self, text: str) -> Generator:
            PATTERN = r"Dz\.\s*U\..*?$"
            PATTERN_YEAR = r"(z ([0-9]{4}) r\..*?)(?=z [0-9]{4} r\.|$)"
            PATTERN_NR_GROUP = r"Nr [0-9]+.*?(?=Nr|$|z [0-9]{4} r)"
            PATTERN_NR = r"Nr ([0-9]+)"
            PATTERN_POZ = r"(?<![\S\[])([0-9]+)"
            PATTERN_RE = re.compile(PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE )
            for item in PATTERN_RE.findall(text):
                years = re.findall(PATTERN_YEAR, item, overlapped=True)
                for year in years:
                    nrs = re.findall(PATTERN_NR_GROUP, year[0], overlapped=True)
                    if len(nrs) > 0:
                        for n in nrs:
                            nr = re.search(PATTERN_NR, n)
                            if nr:
                                poz_str = n.split("poz. ")
                                pozs = []
                                for p in poz_str[1:]:
                                    pozs.extend(re.findall(PATTERN_POZ, p))
                                for p in pozs:
                                    law = self.LawEntry(item, year[1], p, nr.group(1))
                                    yield law
                    else:
                        poz_str = year[0].split("poz. ")
                        pozs = []
                        for p in poz_str[1:]:
                            pozs.extend(re.findall(PATTERN_POZ, p))
                    for p in pozs:
                        law = self.LawEntry(item, year[1], p)
                        yield law
                #yield item

    def extract_html(self, soup: BeautifulSoup) -> LawDoc:
        law_doc = self._get_law_doc(soup)
        return law_doc

    def _get_law_doc(self, soup: BeautifulSoup) -> LawDoc:
        if soup.find("link", attrs={"href": "./text_files/ISAP-isap_txt.css"}):
            law_doc = self.ISAPLawDoc(soup, self)
        else:
            law_doc = self.GenericPolishLawDoc(soup, self)
        return law_doc

    def _replace_bad_chars(self, text: str) -> str:
        for k, v in self.BAD_CHARS_TO_REPLACE.items():
            text = text.replace(k, v)
        return text

    def _clean_html(self, html_string: str) -> str:
        return self._replace_bad_chars(
            re.sub(
                self.PATTERN_WHITESPACE,
                " ",
                re.sub(self.PATTERN_CLEAN_HMTL, "", str(html_string)),
            ).strip(),
        ).strip()

