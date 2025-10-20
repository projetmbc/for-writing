from collections import defaultdict
import re
import yaml
import textwrap
from pprint import pprint

markdown_text = """
<!--
inlincode:
  - lang: XXX
    what:
      - YYY
-->

Use a luadraw palette
---------------------
<!--
inlincode:
  - lang: lua
    what:
      - palGistHeat
-->

The palette names all use the prefix `pal` followed by the name available in the file `at-prism.json`. You can acces a palette by two ways.
<!--
inlincode:
  - lang: lua
    what:
      - getPal("GistHeat")
      - getPal("palGistHeat")
-->
  * `palGistHeat` is a palette variable.
"""

# Regex pour capturer les blocs inlincode
pattern = re.compile(r'<!--\s*(inlincode:.*?)-->', re.DOTALL)

matches = pattern.findall(markdown_text)

inlincode_blocks = []
for block in matches:
    # Dé-denter pour corriger l'indentation YAML
    block = textwrap.dedent(block)
    try:
        data = yaml.safe_load(block)
        inlincode_blocks.append(data['inlincode'])
    except yaml.YAMLError as e:
        print("Erreur YAML :", e)

result = defaultdict(list)

for block in inlincode_blocks:
    for item in block:
        lang = item['lang']
        what = item.get('what', [])
        result[lang].extend(what)


pprint(result)
