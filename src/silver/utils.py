from pyspark.sql import functions as F


def limpar_comentario(coluna):
    texto_limpo = F.trim(F.regexp_replace(coluna.cast("string"), r"\s+", " "))
    return F.when(texto_limpo == "", F.lit(None)).otherwise(texto_limpo)

def limpar_nomes(coluna):

    com_acento = "áàâãéèêíïóòôõúùûçÁÀÂÃÉÈÊÍÏÓÒÔÕÚÙÛÇ"
    sem_acento = "aaaaeeeiiExternaloooouuucAAAAEEEIIOOOOUUUC"
    col_sem_acento = F.translate(coluna, com_acento, sem_acento)

    col_limpa = F.trim(F.regexp_replace(col_sem_acento, r"\s+"," "))

    col_final = F.initcap(col_limpa)

    conectores = ["De","Do","Da","Dos","Das"]

    for conector in conectores:
        col_final = F.regexp_replace(col_final,rf"\b{conector}\b",conector.lower())

    return col_final
