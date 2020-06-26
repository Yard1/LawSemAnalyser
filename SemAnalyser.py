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
import shutil

import json
import subprocess
from tqdm import tqdm
import docker

from HTMLExtractor import HTMLExtractor


class SemAnalyser(object):
    def __init__(
        self,
        data_path: str,
        html_docs_path: str,
        html_extractor=HTMLExtractor(),
        temp_path="temp",
        output_path="out",
        json_output_path=os.path.join("out", "json"),
        liner2_output_path=os.path.join("out", "liner2"),
        docker_image="yard1/liner2-cli:latest",
    ):
        self.data_path = data_path
        self.html_docs_path = html_docs_path
        self.html_extractor = html_extractor
        self.temp_path = temp_path
        self.output_path = output_path
        self.json_output_path = json_output_path
        self.liner2_output_path = liner2_output_path
        self.docker_image = docker_image
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        if not os.path.exists(self.json_output_path):
            os.makedirs(self.json_output_path)

        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        os.makedirs(self.temp_path)
        if os.path.exists(self.liner2_output_path):
            shutil.rmtree(self.liner2_output_path)
        os.makedirs(self.liner2_output_path)
        self.docker_client = docker.from_env()
        # self.docker_client.images.pull(docker_image)

    def analyseDocs(self):
        self._prepare_docs()
        self._run_liner2()
        self._load_liner2_output()
        self._save_txt_files()

    def _prepare_docs(self):
        print("Generating files ...")
        self.html_files = self._read_html_files()
        self.html_data = self._extract_from_html()
        self._save_txt_files()

    def _save_txt_files(self):
        for file_name, data in self.html_data.items():
            path = os.path.join(self.json_output_path, file_name + ".json")
            print("Saving txt file " + path + "...")
            with codecs.open(path, "w", encoding="utf8") as output_file:
                json.dump(
                    data.result, output_file, ensure_ascii=False, separators=(",", ":")
                )

    def _read_html_files(self) -> dict:
        html_files = {}
        for name in os.listdir(self.html_docs_path):
            print("Reading file " + os.path.join(self.html_docs_path, name) + "...")
            if os.path.isfile(os.path.join(self.html_docs_path, name)):
                try:
                    with codecs.open(
                        os.path.join(self.html_docs_path, name), encoding="utf-8"
                    ) as input_file:
                        html_files[name] = BeautifulSoup(input_file, "lxml")
                except UnicodeDecodeError:
                    with codecs.open(
                        os.path.join(self.html_docs_path, name), encoding="iso-8859-2"
                    ) as input_file:
                        html_files[name] = BeautifulSoup(input_file, "lxml")
        return html_files

    def _extract_from_html(self) -> collections.defaultdict:
        data_collections = collections.defaultdict(collections.OrderedDict)
        for file_name in self.html_files:
            print(
                "Processing html file "
                + os.path.join(self.html_docs_path, file_name)
                + "..."
            )
            data_collections[file_name] = self.html_extractor.extract_html(
                self.html_files[file_name]
            )

        return data_collections

    def _prepare_liner2_input(self):
        for filename, data in self.html_data.items():
            print(f"Preparing {filename} for liner2...")
            data = data.result["document"]
            for element in tqdm(data["elements"] + data["references"]):
                if "subelements" in element:
                    for subelement in element["subelements"]:
                        subelement["liner2"] = self._save_text_for_liner2(
                            subelement["content"],
                            f"{filename}.{element['type']}.{element['id']}.{subelement['type']}.{subelement['id']}",
                        )
                element["liner2"] = self._save_text_for_liner2(
                    element["content"], f"{filename}.{element['type']}.{element['id']}"
                )

    def _save_text_for_liner2(self, text: str, filename: str):
        with codecs.open(f"temp/{filename}.txt", "w", encoding="utf8") as f:
            f.write(re.sub(r"_REP_\w+", "", text.strip()).strip())

    def _append_liner2_output(self, element, liner2_output):
        try:
            if (
                "liner2" in element
                and element["liner2"]
                and "annotations" in element["liner2"]
            ):
                element["liner2"]["annotations"].extend(liner2_output["annotations"])
                if element["liner2"]["annotations"]:
                    element["liner2"]["annotations"].sort(
                        key=lambda x: int(x["tokens"][0][1:])
                    )
                    for i, x in enumerate(element["liner2"]["annotations"]):
                        x["id"] = f"a{i+1}"
            else:
                element["liner2"] = liner2_output.copy()
        except:
            element["liner2"] = liner2_output.copy()

    def _load_liner2_output(self):
        for name in tqdm(sorted(os.listdir(self.liner2_output_path))):
            liner2_output = None
            with open(os.path.join(self.liner2_output_path, name), "r") as f:
                liner2_output = json.load(f)
            current_html_file = None
            for html_filename in self.html_data.keys():
                if name.startswith(html_filename):
                    current_html_file = html_filename
                    break
            if not current_html_file:
                print(f"{name} doesn't match any html file")
                continue
            element_name = name.replace(current_html_file, "", 1)[1:-9].split(".")
            if len(element_name) > 2:
                subelement_name = (element_name[2], element_name[3])
                element_name = (element_name[0], element_name[1])
            elements = self.html_data[current_html_file].result["document"]["elements"]
            references = self.html_data[current_html_file].result["document"][
                "references"
            ]
            element = next(
                (
                    x
                    for x in elements + references
                    if x["type"] == element_name[0] and str(x["id"]) == element_name[1]
                ),
                None,
            )
            if element:
                if "subelements" in element:
                    subelement = next(
                        (
                            x
                            for x in element["subelements"]
                            if x["type"] == subelement_name[0]
                            and str(x["id"]) == subelement_name[1]
                        ),
                        None,
                    )
                    if subelement:
                        self._append_liner2_output(subelement, liner2_output)
                else:
                    self._append_liner2_output(element, liner2_output)
            else:
                element = next(
                    (
                        x
                        for x in elements + references
                        if x["type"] == element_name[0]
                        and str(x["id"]) == element_name[1]
                    ),
                    None,
                )
                if element:
                    self._append_liner2_output(element, liner2_output)

    def _run_liner2(self):
        self._prepare_liner2_input()
        print(f"Running Docker {self.docker_image}...")
        self.docker_client.containers.run(
            self.docker_image,
            entrypoint="/liner2/liner2-batch.sh",
            userns_mode="host",
            volumes={
                f"{os.getcwd()}/{self.temp_path}": {
                    "bind": "/liner2/input",
                    "mode": "rw",
                },
                f"{os.getcwd()}/{self.liner2_output_path}": {
                    "bind": "/liner2/output",
                    "mode": "rw",
                },
                tempfile.gettempdir(): {"bind": "/tmp", "mode": "rw"},
            },
        )
        print(f"Done running Docker {self.docker_image}...")
