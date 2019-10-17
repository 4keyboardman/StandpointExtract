import re


def load_text_summarization_rules(rules_path):
    res = []
    with open(rules_path, encoding='utf-8') as f:
        for line in f:
            splits = line.split('->')
            condition = splits[0].strip()
            replacements = splits[1].strip().split('    ')
            res.append((condition, replacements))
    return res


rules = load_text_summarization_rules(r'D:\development\jupyter\StandpointExtract\instance\text_summarization_rules.txt')
for i in rules:
    print(i)
