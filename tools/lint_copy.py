#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linter de redacción "anti-IA" para los textos de la web.

Busca en el texto visible (y en title, meta description, og/twitter y alt)
los rasgos que delatan texto generado por IA en castellano: vocabulario
inflado, estructuras tipo "No es X, es Y", "no solo... sino también",
preguntas-puente, cierres-resumen, rayas usadas como conector, emojis...

Ningún rasgo aislado demuestra nada: lo que delata es la acumulación. Por
eso hay tres niveles:
  - PROHIBIDO: casi siempre delata. Con --strict hace fallar el script.
  - ESTRUCTURA: patrones sintácticos típicos. Aviso.
  - VOCABULARIO: palabras sospechosas. Solo se avisa si una página supera
    el umbral de densidad (DENSITY_LIMIT apariciones).

Uso:
    python tools/lint_copy.py            # informe, nunca falla
    python tools/lint_copy.py --strict   # falla si hay algo PROHIBIDO
    python tools/lint_copy.py archivo.html otro.html

Las reglas salen de la investigación sobre rasgos de escritura de LLMs
(Wikipedia "Signs of AI writing", Kobak et al. 2025, listas de "slop"
en castellano). Hay que revisarlas cada cierto tiempo: los tics cambian
con cada generación de modelos.
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_sitemap import find_pages  # noqa: E402

FLAGS = re.IGNORECASE | re.UNICODE

PROHIBITED = {
    "calco de 'delve' (sumergirse, adentrarse, ahondar)": r"\b(sumérge(te|nos)|sumergirse|adentr(arse|émonos|ate)|ahond(ar|emos))\b",
    "metáfora vacía (tapiz, crisol, sinfonía, faro)": r"\b(tapiz|crisol|sinfonía|faro que guía)\b",
    "'desbloquear'": r"\bdesbloque(a|ar|ando)\b",
    "'liberar/aprovechar el poder/potencial'": r"\b(liberar|aprovechar|desatar)\s+(todo\s+)?el\s+(poder|potencial)\b",
    "'al siguiente nivel'": r"\b(siguiente|próximo|otro)\s+nivel\b",
    "apertura 'en el vertiginoso mundo de...'": r"\ben\s+(el|este|un)\s+(vertiginoso|cambiante|dinámico|competitivo|actual)\s+(mundo|panorama|entorno|paisaje)\b",
    "'en la era de...'": r"\ben\s+la\s+era\s+(de|digital)\b",
    "'en un mundo donde...'": r"\ben\s+un\s+mundo\s+(donde|en\s+el\s+que|cada\s+vez\s+más)\b",
    "relleno temporal ('hoy en día', 'en el contexto actual')": r"\b(hoy\s+en\s+día|en\s+el\s+mundo\s+actual|en\s+el\s+contexto\s+actual|en\s+el\s+presente\s+contexto)\b",
    "calco de 'testament' ('es un testimonio de')": r"\b(un|es\s+un)\s+testimonio\s+de\b",
    "'juega un papel clave/fundamental'": r"\b(juega|desempeña)\s+un\s+(papel|rol)\s+(clave|fundamental|crucial|esencial|vital|importante)\b",
    "importancia inflada ('cambia las reglas del juego', 'un antes y un después')": r"\bcambi(a|ar|ará)\s+las\s+reglas\s+del\s+juego\b|\bun\s+antes\s+y\s+un\s+después\b",
    "cierre-resumen ('en resumen', 'en definitiva')": r"\b(en\s+resumen|en\s+conclusión|en\s+definitiva|para\s+concluir|en\s+pocas\s+palabras)\b",
    "residuo de chat": r"\b(espero\s+que\s+(esto|te)\s+(sea|resulte)|como\s+modelo\s+de\s+lenguaje|aquí\s+tienes)\b",
    "jerga de folleto ('sin fisuras', 'de vanguardia', 'holístico', 'sinergia')": r"\b(sin\s+fisuras|sin\s+costuras|de\s+vanguardia|holístic[oa]s?|sinergias?)\b",
    "calco del inglés ('hacer sentido', 'hacer la diferencia')": r"\bhacer\s+(sentido|la\s+diferencia)\b",
    "artefacto de cita de un LLM": r"oaicite|contentReference|turn0search\d|\[cite:\s*\d+\]|utm_source=chatgpt",
}

STRUCTURE = {
    "antítesis 'No es X, es Y'": r"\bno\s+(es|son|se\s+trata\s+de|vendemos|hacemos)\b[^.!?]{1,80}[.,;:]\s*(es|son|sino|se\s+trata\s+de|vendemos|hacemos)\b",
    "'no solo X, sino también Y'": r"\bno\s+(solo|sólo|solamente|únicamente)\b[^.!?]{1,100}\bsino\s+(también|que)\b",
    "'la pregunta no es...'": r"\bla\s+(pregunta|cuestión)\s+no\s+es\b",
    "pregunta-puente ('¿El resultado?')": r"¿(El|La|Los|Las|Y)\s+\w+(\s+\w+)?\?",
    "ráfaga de negaciones ('Sin X. Sin Y.')": r"(\bSin\s+\w+\.\s*){2,}",
    "dos puntos con redoble ('La respuesta es sencilla:')": r"\b(la\s+respuesta\s+es\s+(sencilla|simple|clara)|te\s+lo\s+explicamos|a\s+continuación)\s*:",
    "sinceridad anunciada": r"\b(seamos\s+honestos|la\s+verdad\s+es\s+que|sinceramente|honestamente)\b",
    "atribución vaga ('los expertos', 'diversos estudios')": r"\b(los\s+expertos|diversos\s+estudios|numerosos\s+estudios|muchos\s+coinciden)\b",
    "cautela en cascada ('podría potencialmente')": r"\bpodría\s+(potencialmente|posiblemente)\b",
    "CTA genérico": r"\b(descubre\s+(más|cómo)|¿listo\s+para|¿estás\s+preparado|empieza\s+tu\s+transformación)\b",
}

VOCABULARY = {
    "intensificadores (clave, crucial, fundamental...)": r"\b(clave|crucial(es)?|fundamental(es)?|esencial(es)?|vital(es)?|primordial(es)?)\b",
    "verbos inflados (potenciar, impulsar, optimizar...)": r"\b(potenci(ar|a|amos|an)|impuls(ar|a|amos|an)|fomentar|optimiz(ar|a|amos|an)|maximiz(ar|a)|revolucion(ar|a))\b",
    "sustantivos de folleto (transformación, innovación, robusto...)": r"\b(transformación|transformar|innovación|innovador(a|es)?|robust[oa]s?|escalables?|integral(es)?)\b",
    "verbos figurados (navegar, embarcarse, empoderar, elevar)": r"\b(navegar|embarcar(se|te)|empoderar|elevar)\b",
    "'subraya/resalta/pone de manifiesto'": r"\b(subraya|resalta|pone\s+de\s+manifiesto|evidencia)\b",
    "conectores de relleno (además, asimismo, cabe destacar...)": r"\b(además|adicionalmente|asimismo|cabe\s+(destacar|señalar|mencionar)|es\s+importante\s+(destacar|señalar|tener\s+en\s+cuenta)|vale\s+la\s+pena\s+(señalar|destacar)|sin\s+(lugar\s+a\s+)?dudas?|indudablemente|ciertamente)\b",
    "frases hechas del sector (te acompañamos, resultados reales, a medida...)": r"\b(te\s+acompaña(mos)?|en\s+cada\s+paso|resultados\s+reales|a\s+medida|soluciones\s+(integrales|innovadoras|tecnológicas))\b",
    "autobombo (apasionados, líderes en, expertos en)": r"\b(apasionad[oa]s?|líderes\s+en|expertos\s+en)\b",
}
DENSITY_LIMIT = 3  # apariciones por página a partir de las cuales se avisa

EM_DASH = re.compile(r"\S\s?—\s?\S")
EMOJI_ARROWS = re.compile(r"[→⇒➜✅✔🚀💡🔥✨📈📊🎯👉]")
LABEL_MAX_WORDS = 5  # textos cortos (etiquetas de diseño como "01 — Datos") no cuentan como prosa

TEXT_META = {"description", "og:title", "og:description", "twitter:title", "twitter:description"}


class TextExtractor(HTMLParser):
    """Recoge (línea, texto) de todo lo que lee una persona o un buscador."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "svg"):
            self._skip += 1
        if tag == "meta" and (a.get("name") or a.get("property")) in TEXT_META:
            self.chunks.append((self.getpos()[0], a.get("content", "")))
        if tag == "img" and a.get("alt"):
            self.chunks.append((self.getpos()[0], a["alt"]))

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if text and not self._skip:
            self.chunks.append((self.getpos()[0], text))


def lint(path):
    parser = TextExtractor()
    parser.feed(path.read_text(encoding="utf-8"))
    findings = {"PROHIBIDO": [], "ESTRUCTURA": [], "VOCABULARIO": [], "CARACTERES": []}
    vocabulary_hits = {}

    for line, text in parser.chunks:
        for label, pattern in PROHIBITED.items():
            for m in re.finditer(pattern, text, FLAGS):
                findings["PROHIBIDO"].append((line, label, m.group(0)))
        for label, pattern in STRUCTURE.items():
            for m in re.finditer(pattern, text, FLAGS):
                findings["ESTRUCTURA"].append((line, label, m.group(0)))
        for label, pattern in VOCABULARY.items():
            for m in re.finditer(pattern, text, FLAGS):
                vocabulary_hits.setdefault(label, []).append((line, m.group(0)))
        is_prose = len(text.split()) > LABEL_MAX_WORDS
        if is_prose and EM_DASH.search(text):
            findings["CARACTERES"].append((line, "raya larga (—) en prosa: usa coma, punto o paréntesis", text[:70]))
        for m in EMOJI_ARROWS.finditer(text):
            if is_prose:
                findings["CARACTERES"].append((line, "emoji o flecha en prosa", m.group(0)))
        if is_prose and text.count("!") > 0:
            findings["CARACTERES"].append((line, "exclamación", text[:70]))

    for label, hits in vocabulary_hits.items():
        if len(hits) >= DENSITY_LIMIT:
            words = ", ".join(sorted({w.lower() for _, w in hits}))
            findings["VOCABULARIO"].append((hits[0][0], f"{label}: {len(hits)} veces", words))
    return findings


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--strict", action="store_true", help="falla si hay algo PROHIBIDO")
    args = parser.parse_args()

    files = [f.resolve() for f in args.files] or [ROOT / rel for rel in find_pages()]
    prohibited = 0
    for path in files:
        findings = lint(path)
        total = sum(len(v) for v in findings.values())
        print(f"\n{path.relative_to(ROOT).as_posix()}: {total} hallazgos")
        for level, items in findings.items():
            for line, label, sample in sorted(items):
                print(f"  {level:<11} L{line:<4} {label}  ->  {sample!r}")
        prohibited += len(findings["PROHIBIDO"])

    if args.strict and prohibited:
        sys.exit(f"\n{prohibited} expresiones PROHIBIDAS. Reescribe esos textos.")


if __name__ == "__main__":
    main()
