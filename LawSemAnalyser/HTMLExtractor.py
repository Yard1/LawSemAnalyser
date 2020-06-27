# coding: UTF-8
from typing import Generator
import regex as re
from bs4 import BeautifulSoup, NavigableString


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

    class PolishLawDoc(LawDoc):
        def __init__(self, soup: BeautifulSoup, extractor):
            self.type = "Polish"
            super().__init__(soup, extractor)

        def _extract(self):
            glossary = self.result["document"]["glossary"]
            body = self.result["document"]["body"]
            soup = self.soup.find("body")

            section = soup.find("h1")
            title_element = []
            introduction_element = []
            for child in section.children:
                title_element.append(child.contents[0])
                if len(child.contents) > 1:
                    introduction_element.append(child.contents[1])
            element = {
                "type": "title",
                "id": 0,
                "content": title_element,
                "links": [],
            }
            body.append(element)
            element = {
                "type": "introduction",
                "id": 0,
                "content": introduction_element,
                "links": [],
            }
            body.append(element)

            sections = soup.find_all("section", id=re.compile(r"part_[0-9]+"))
            section = sections[0]
            chapters = section.find("div", "block").find_all(
                attrs={"class": "unit_chpt"}, recursive=False
            )
            for chapter in chapters:
                header = chapter.find_all("p", recursive=False)
                element = {
                    "type": "chapter",
                    "id": chapter.attrs["data-id"],
                    "content": list(header),
                    "links": [],
                }
                body.append(element)
                div_inner = chapter.find("div")
                articles = div_inner.find_all(
                    lambda x: x.has_attr("class") and "unit_arti" in x["class"],
                    recursive=False,
                )
                for article in articles:
                    links = article.find_all("a")

                    element = {
                        "type": "article",
                        "id": article.attrs["data-id"],
                        "content": [article],
                        "links": [],
                    }
                    body.append(element)

            glossary_html = section.find("div", "gloss-section").find_all(
                "div", attrs={"class": "gloss"}, recursive=False
            )
            for gloss in glossary_html:
                element = {
                    "type": "gloss",
                    "id": gloss.attrs["id"],
                    "content": gloss.contents,
                    "links": [],
                }
                glossary.append(element)

            appendices = sections[1:] if len(sections) > 1 else []

            for appendix in appendices:
                appendix = appendix.find("div", attrs={"class": "part"})
                element = {
                    "type": "appendix",
                    "id": appendix.attrs["id"],
                    "content": [appendix],
                    "links": [],
                }
                body.append(element)

            for element in body + glossary:
                for child in element["content"]:
                    if isinstance(child, NavigableString):
                        continue
                    for link in child.find_all("a"):
                        external = False
                        if link.attrs["href"][0] == "#":
                            external = True
                            address = link.attrs["href"][1:]
                        else:
                            address = link.attrs["href"]
                        element["links"].append(
                            {
                                "text": self.extractor._clean_html(link),
                                "address": address,
                                "is_external": external,
                            }
                        )
            self.html_result["document"]["body"] = body.copy()
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

    def extract_html(self, soup: BeautifulSoup) -> LawDoc:
        law_doc = self._get_law_doc(soup)
        return law_doc

    def _get_law_doc(self, soup: BeautifulSoup) -> LawDoc:
        law_doc = self.PolishLawDoc(soup, self)
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
                re.sub(
                    self.PATTERN_CLEAN_HMTL, "", re.sub("&nbsp;", " ", str(html_string))
                ),
            ).strip()
        )
