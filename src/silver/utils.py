import unicodedata
import numpy as np
import pandas as pd


def limpar_nome_cidade(texto):
    if pd.isna(texto):
        return texto

    texto_normalizado = unicodedata.normalize("NFD", str(texto))
    texto_sem_acento = "".join(
        c for c in texto_normalizado if unicodedata.category(c) != "Mn"
    )
    texto_limpo = " ".join(texto_sem_acento.split())
    texto_final = texto_limpo.title()

    conectores = [" De ", " Do ", " Da ", " Dos ", " Das "]
    for conector in conectores:
        texto_final = texto_final.replace(conector, conector.lower())

    return texto_final


def limpar_comentario(texto):
    if pd.isna(texto):
        return texto
    texto_limpo = " ".join(str(texto).split())
    return texto_limpo if texto_limpo else np.nan