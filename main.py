import time
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import deepl
import pysrt
from tqdm import tqdm

from dotenv import load_dotenv
import os

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

if not DEEPL_API_KEY:
    raise ValueError("DEEPL_API_KEY not found in .env")

SRT_PATH = Path(r"E:\test.srt")
DEST_PATH = Path(r"E:\test2.srt")

SOURCE_LANG = "EN"
TARGET_LANG = "VI"
MAX_WORKERS = 4
RETRY_COUNT = 3
DELAY_SECONDS = 0.2


translator = deepl.Translator(DEEPL_API_KEY)


def clean_text(text: str) -> str:
    """Clean subtitle text before translation."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_text(text: str) -> str:
    """Translate text with retry limit."""
    if not text.strip():
        return text

    for attempt in range(RETRY_COUNT):
        try:
            result = translator.translate_text(
                text,
                source_lang=SOURCE_LANG,
                target_lang=TARGET_LANG,
            )
            return result.text.strip()
        except Exception as e:
            if attempt == RETRY_COUNT - 1:
                print(f"Translate failed: {text[:80]}... | Error: {e}")
                return text

            time.sleep(1 + attempt)

    return text


def translate_subtitle(index, sub):
    """Translate one subtitle block."""
    original_text = clean_text(sub.text)
    translated_text = translate_text(original_text)

    time.sleep(DELAY_SECONDS)

    return index, translated_text


def main():
    subs = pysrt.open(str(SRT_PATH), encoding="utf-8")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(translate_subtitle, index, sub)
            for index, sub in enumerate(subs)
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Translating"):
            index, translated_text = future.result()
            subs[index].text = translated_text

    subs.save(str(DEST_PATH), encoding="utf-8")
    print(f"Done: {DEST_PATH}")


if __name__ == "__main__":
    main()