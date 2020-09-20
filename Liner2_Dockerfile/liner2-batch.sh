#!/usr/bin/env bash
find /liner2/input -name *.txt | parallel --verbose "wcrft-app nkjp_e2.ini -i text -o ccl {} -O {}.tag"

find /liner2/input -name *.tag | parallel --verbose "./liner2-cli pipe -i ccl -o json -f {} -m liner25_model_ner_rev1/config-top9.ini > /liner2/output/{/}.top9.json"

find /liner2/input -name *.tag | parallel --verbose "./liner2-cli pipe -i ccl -o json -f {} -m timex_model_full/timex_model_full/cfg.ini > /liner2/output/{/}.timex.json"