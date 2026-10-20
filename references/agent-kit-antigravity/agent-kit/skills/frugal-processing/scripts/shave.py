import sys
import re

def shave_text(text):
    # 1. Suppression des espaces multiples et tabulations
    text = re.sub(r'[ \t]+', ' ', text)
    # 2. Suppression des sauts de ligne excessifs
    text = re.sub(r'\n\s*\n', '\n', text)
    # 3. Suppression des commentaires style HTML/XML
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # 4. Réduction des répétitions de caractères (ex: !!! -> !)
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    return text.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
            print(shave_text(content))
