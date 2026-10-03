"""Gera privacy-policy.html (PT/EN/ES) usando somente a biblioteca padrão."""

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {
    "pt": ("pt-BR", "Política de Privacidade", "Idioma da política de privacidade"),
    "en": ("en", "Privacy Policy", "Privacy policy language"),
    "es": ("es", "Política de Privacidad", "Idioma de la política de privacidad"),
}
LINKS = re.compile(r"https://[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


def linkify(text):
    result = []
    start = 0
    for match in LINKS.finditer(text):
        result.append(escape(text[start:match.start()]))
        label = match.group()
        href = label if label.startswith("https://") else "mailto:" + label
        result.append(f'<a href="{escape(href, quote=True)}">{escape(label)}</a>')
        start = match.end()
    result.append(escape(text[start:]))
    return "".join(result)


def render(text):
    blocks = []
    for paragraph in text.strip().split("\n\n"):
        if re.fullmatch(r"\d+\. [^\n]+", paragraph):
            blocks.append(f"<h2>{escape(paragraph)}</h2>")
            continue
        lines = paragraph.splitlines()
        bullets = next((i for i, line in enumerate(lines) if line.startswith("• ")), None)
        if bullets is None:
            blocks.append(f"<p>{linkify(paragraph)}</p>")
        else:
            if bullets:
                blocks.append(f"<p>{linkify(' '.join(lines[:bullets]))}</p>")
            blocks.append("<ul>" + "".join(f"<li>{linkify(line.removeprefix('• '))}</li>"
                                          for line in lines[bullets:]) + "</ul>")
    return "\n".join(blocks)


def main():
    sections = []
    for language, (tag, title, label) in LANGUAGES.items():
        text = (ROOT / "content" / f"{language}.txt").read_text(encoding="utf-8")
        assert len(re.findall(r"(?m)^\d+\. ", text)) == 10, language
        assert "Cyberware Tecnologias LTDA" in text, language
        assert "Imagens com Frases" in text, language
        assert "cyberware.tecnologias@gmail.com" in text, language
        sections.append(f'<section id="{language}" lang="{tag}" aria-labelledby="title-{language}">\n'
                        f'<h1 id="title-{language}">{escape(title)}</h1>\n'
                        '<p class="dim">Cyberware Tecnologias LTDA</p>\n'
                        f'<article class="card">\n{render(text)}\n</article>\n</section>')
    template = (ROOT / "scripts/page-template.html").read_text(encoding="utf-8")
    html = template.replace("<!-- POLICY_SECTIONS -->", "\n".join(sections))
    (ROOT / "privacy-policy.html").write_text(html, encoding="utf-8")
    print("privacy-policy.html gerado: Português, English, Español")


if __name__ == "__main__":
    main()
