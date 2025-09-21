import re

def parse_key(df, selected_column):
    key_map = {}
    for row in df[selected_column].dropna():
        text = str(row).strip().lower()
        match = re.match(r"(\d+)[\.\-\s]*([a-e](?:,[a-e])*)", text)
        if match:
            qnum = int(match.group(1))
            raw_ans = match.group(2)
            valid = [opt for opt in raw_ans.split(",") if opt in {"a", "b", "c", "d", "e"}]
            if valid:
                key_map[qnum] = ",".join(valid)
    return key_map