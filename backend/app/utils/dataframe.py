from __future__ import annotations

from typing import Optional, Tuple, Dict

import pandas as pd


DATE_CANDIDATES = ["Date", "年月日", "date"]
STORE_CANDIDATES = ["shop", "店舗名", "store", "Shop"]

DISPLAY_NAME_MAP: Dict[str, str] = {
    "Mens_JACKETS&OUTER2": "メンズ ジャケット・アウター",
    "Mens_KNIT": "メンズ ニット",
    "Mens_PANTS": "メンズ パンツ",
    "WOMEN'S_JACKETS2": "レディース ジャケット",
    "WOMEN'S_TOPS": "レディース トップス",
    "WOMEN'S_ONEPIECE": "レディース ワンピース",
    "WOMEN'S_bottoms": "レディース ボトムス",
    "WOMEN'S_SCARF & STOLES": "レディース スカーフ・ストール",
}


def detect_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in df.columns:
            return cand
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def detect_date_and_store(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    return detect_column(df, DATE_CANDIDATES), detect_column(df, STORE_CANDIDATES)


def display_name_for(category: str) -> str:
    return DISPLAY_NAME_MAP.get(category, category)

