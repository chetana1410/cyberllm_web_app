from handle_error import log_error
from unstructured.cleaners.core import (
    replace_unicode_quotes,
    bytes_string_to_string,
    clean,
    clean_non_ascii_chars,
    group_broken_paragraphs,
)
from unstructured.cleaners.translate import translate_text

def clean_elements(elements):
    try:
        for element in elements:
            # Apply each cleaning function
            element.apply(replace_unicode_quotes)
            try:
                element.apply(lambda x: bytes_string_to_string(x, encoding="utf-8"))
            except:
                pass
            try:
                element.apply(lambda x: clean(x, bullets=False, extra_whitespace=True, dashes=False, trailing_punctuation=False, lowercase=False))
            except:
                pass
            try:
                element.apply(clean_non_ascii_chars)
            except:
                pass
            try:
                element.apply(group_broken_paragraphs)
            except:
                pass
            try:
                if 'eng' not in element.Metadata.languages:
                    element.apply(translate_text)
            except:
                pass
        return elements
    except Exception as e:
        log_error(f"Error : {e}")