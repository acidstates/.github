#!/usr/bin/env python3
"""Генератор фирменной схемы «Platform at a glance» для витрины организации.

Одна геометрия — две темы (light/dark), подключаются в profile/README.md через <picture>,
как логотип ACID//STATES. Схема печётся рукописным SVG, а не mermaid, намеренно: витрина
GitHub не рендерит mermaid вовсе, а стилизовать его под канон бренда (бумага/чернила,
кислотный #C6F000, жёсткие офсет-тени, халфтон) нельзя нигде. Примитивы и палитры — те же,
что у `frameworks/gamecore/tools/render_round_diagram.py` в acidstates/platform.

Запуск (из корня репозитория .github):
    python3 profile/tools/render_platform_diagram.py          # → profile/assets/
    python3 profile/tools/render_platform_diagram.py <dir>    # → куда сказали

Меняется устройство платформы — правь ЗДЕСЬ и перегенерируй оба файла; руками SVG не трогать.
"""
import pathlib
import sys

DARK = dict(
    bg="#121417", panel="#181B1F", panel2="#1D2126", ink="#E7E3DA",
    ink2="#A8AEB5", ink3="#767C83", acid="#C6F000", acidink="#121417",
    hot="#C6F000", shadow="#000000", shadow_op="0.55", dots="#E7E3DA",
    srv="#9FBF3B",
)
LIGHT = dict(
    bg="#E9E5DC", panel="#F4F2EC", panel2="#EDEAE1", ink="#171A1D",
    ink2="#4A4F55", ink3="#767C83", acid="#C6F000", acidink="#171A1D",
    hot="#3F6B00", shadow="#171A1D", shadow_op="0.85", dots="#171A1D",
    srv="#4F7A00",
)

MONO = "'SFMono-Regular','Menlo','Consolas','Liberation Mono',monospace"
SANS = "'Helvetica Neue','Arial',sans-serif"


def panel(x, y, w, h, p, rot=0.0, fill=None, dash=None, sw=2.6):
    fill = fill or p["panel"]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    cx, cy = x + w / 2, y + h / 2
    return (f'<g transform="rotate({rot} {cx} {cy})">'
            f'<rect x="{x+7}" y="{y+7}" width="{w}" height="{h}" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{p["ink"]}" stroke-width="{sw}"{d}/>')


def text(x, y, s, size, p, fill=None, w="normal", fam=MONO, ls="0", anchor="start", op="1"):
    fill = fill or p["ink"]
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" '
            f'fill="{fill}" letter-spacing="{ls}" text-anchor="{anchor}" opacity="{op}">{s}</text>')


def eyebrow(x, y, s, p, fill=None):
    return text(x, y, s.upper(), 10.5, p, fill or p["ink3"], w="bold", ls="1.6")


def chip(x, y, w, s, p, hot=False):
    fill = p["acid"] if hot else p["panel2"]
    ink = p["acidink"] if hot else p["ink2"]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="21" fill="{fill}" stroke="{p["ink"]}" stroke-width="1.2"/>'
            + text(x + w / 2, y + 14.5, s, 10.5, p, ink, anchor="middle", w="bold" if hot else "normal"))


def edge_label(x, y, s, p, anchor="start"):
    w = len(s) * 6.3 + 10
    lx = x - (w / 2 if anchor == "middle" else (w if anchor == "end" else 0))
    return (f'<rect x="{lx-2}" y="{y-11}" width="{w}" height="15" fill="{p["bg"]}" opacity="0.92"/>'
            + text(x, y, s, 9.5, p, p["ink3"], anchor=anchor))


def arrow(pts, p, color=None, width=2.6, dash=None, marker="m"):
    color = color or p["ink"]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    path = "M" + " L".join(f"{x} {y}" for x, y in pts)
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}"{d} marker-end="url(#{marker})"/>'


def box(o, x, y, w, lines, p, title_size=13, sw=1.8, shadow=False):
    """Карточка: жирный заголовок + строки описания. Возвращает высоту."""
    hh = 30 + 15 * len(lines[1:]) + (4 if len(lines) > 1 else 0)
    if shadow:
        o.append(f'<rect x="{x+5}" y="{y+5}" width="{w}" height="{hh}" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>')
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="{sw}"/>')
    o.append(text(x + 14, y + 21, lines[0], title_size, p, w="bold"))
    for i, ln in enumerate(lines[1:]):
        o.append(text(x + 14, y + 39 + 15 * i, ln, 10.5, p, p["ink2"]))
    return hh


def build(p, theme):
    W, H = 1280, 790
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'role="img" aria-label="Platform at a glance — the monorepo publishes versioned packages, '
             f'game repos install them, a merge to main ships through acidstates/workflows onto the droplet, '
             f'game manifests feed the catalog and the stands">')
    o.append('<title>Platform at a glance · ACID//STATES</title>')
    o.append(f'''<defs>
<marker id="m" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="{p["ink"]}"/></marker>
<marker id="h" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="{p["hot"]}"/></marker>
<pattern id="dots" width="11" height="11" patternUnits="userSpaceOnUse">
  <circle cx="2.2" cy="2.2" r="1.9" fill="{p["dots"]}" opacity="0.16"/></pattern>
</defs>''')
    o.append(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')
    o.append('<rect x="0" y="0" width="560" height="150" fill="url(#dots)"/>')
    o.append(f'<rect x="900" y="{H-180}" width="380" height="180" fill="url(#dots)"/>')

    # ── штамп-заголовок ──────────────────────────────────────────
    o.append('<g transform="rotate(-1.6 250 60)">'
             f'<rect x="46" y="36" width="452" height="52" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>'
             f'<rect x="40" y="30" width="452" height="52" fill="{p["acid"]}" stroke="{p["ink"]}" stroke-width="3"/>'
             + text(64, 66, "PLATFORM AT A GLANCE", 27, p, p["acidink"], w="800", fam=SANS, ls="0.5") + "</g>")
    o.append(eyebrow(46, 112, "acidstates · package → module → own repo → merge to main → live", p))

    hot_eyebrow = p["acid"] if theme == "dark" else p["hot"]

    # ── PLATFORM — монорепо ──────────────────────────────────────
    o.append(panel(40, 170, 270, 480, p, rot=-0.7))
    o.append(eyebrow(60, 198, "platform · the monorepo", p, p["srv"]))
    y = 212
    y += box(o, 60, y, 230, ["frameworks/", "gamecore · TS + PixiJS v8 client", "gamemodule · Python/FastAPI RGS", "audio · the sound passport"], p) + 10
    y += box(o, 60, y, 230, ["shared/", "protocol · core · ui · gc-sdk", "brands · rng · mathengine · simbot"], p) + 10
    y += box(o, 60, y, 230, ["apps/ · stands", "statehub · betmanager + admin", "3 studios, each an MCP server"], p) + 10
    y += box(o, 60, y, 230, ["tools/ · infra/", "registry · vector-fit · guards", "nginx · oauth2-proxy · demo-gate"], p) + 10
    o.append(text(60, 632, "docs/agent — the operating manual", 9.5, p, p["ink3"]))
    o.append("</g>")

    # ── PACKAGES → GAMES ─────────────────────────────────────────
    o.append(panel(360, 160, 520, 490, p, rot=0.0))
    o.append(eyebrow(382, 190, "packages → games · one module per game", p, hot_eyebrow))
    o.append(text(858, 190, "SemVer", 10.5, p, p["ink3"], anchor="end"))
    # published — пунктирная внутренняя панель
    o.append(panel(382, 206, 476, 144, p, fill=p["panel2"], dash="7 5", sw=2))
    o.append(eyebrow(400, 230, "published · versioned", p))
    o.append(f'<rect x="400" y="242" width="216" height="92" fill="{p["panel"]}" stroke="{p["ink"]}" stroke-width="1.8"/>')
    o.append(text(414, 263, "GitHub Packages", 13, p, w="bold"))
    o.append(text(414, 281, "@acidstates/gamecore · protocol", 10.5, p, p["ink2"]))
    o.append(text(414, 296, "core · ui · audio", 10.5, p, p["ink2"]))
    o.append(text(414, 311, "gc-sdk · brands", 10.5, p, p["ink2"]))
    o.append(f'<rect x="626" y="242" width="214" height="92" fill="{p["panel"]}" stroke="{p["ink"]}" stroke-width="1.8"/>')
    o.append(text(640, 263, "PEP 503 · DO Spaces", 13, p, w="bold"))
    o.append(text(640, 281, "acidstates-gamemodule", 10.5, p, p["ink2"]))
    o.append(text(640, 296, "acidstates-simbot", 10.5, p, p["ink2"]))
    o.append("</g>")
    # installed by → game repos
    o.append(arrow([(620, 350), (620, 382)], p, color=p["hot"], marker="h"))
    o.append(edge_label(632, 372, "installed by", p))
    o.append(f'<rect x="387" y="389" width="466" height="150" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>')
    o.append(f'<rect x="382" y="384" width="466" height="150" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="2.4"/>')
    o.append(text(396, 407, "game repos", 13.5, p, w="bold"))
    o.append(text(396, 425, "RGS backend + PixiJS client · sealed payout path (compliance_files)", 10.5, p, p["ink2"]))
    o.append(chip(396, 440, 104, "the-reactor", p)); o.append(chip(506, 440, 74, "solvent", p))
    o.append(chip(586, 440, 118, "game-template", p)); o.append(chip(710, 440, 128, "game-template-2.0", p, hot=True))
    o.append(text(396, 486, "math versions per game · game-manifest.json declares the deploy target", 10.5, p, p["ink2"]))
    o.append(text(396, 502, "game.config.json · sound passport · math passport — facts as data,", 10.5, p, p["ink2"]))
    o.append(text(396, 517, "never read from a game's sources by a stand", 10.5, p, p["ink2"]))
    # catalog
    o.append(arrow([(470, 534), (470, 568)], p, width=2.2))
    o.append(edge_label(482, 559, "game-manifest.json", p))
    o.append(f'<rect x="382" y="570" width="300" height="56" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="1.8"/>')
    o.append(text(396, 592, "catalog", 13, p, w="bold"))
    o.append(text(396, 610, "slug → {module, client} + math versions", 10.5, p, p["ink2"]))
    o.append(text(700, 596, "the stands launch a game", 9.5, p, p["ink3"]))
    o.append(text(700, 610, "from this record, never", 9.5, p, p["ink3"]))
    o.append(text(700, 624, "from a checkout", 9.5, p, p["ink3"]))
    o.append("</g>")

    # ── SHIP ─────────────────────────────────────────────────────
    o.append(panel(930, 160, 310, 490, p, rot=0.7))
    o.append(eyebrow(952, 190, "acidstates/workflows · merge to main", p))
    o.append(f'<rect x="952" y="206" width="266" height="72" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="2.4"/>')
    o.append(text(966, 229, "ci-game", 13.5, p, w="bold"))
    o.append(text(966, 247, "uv sync · ruff · pyright · pytest", 10.5, p, p["ink2"]))
    o.append(text(966, 263, "typecheck · build · test", 10.5, p, p["ink2"]))
    o.append(arrow([(1085, 278), (1085, 296)], p, width=2))
    o.append(f'<rect x="952" y="298" width="266" height="88" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="1.8"/>')
    o.append(text(966, 321, "build → deploy", 13, p, w="bold"))
    o.append(text(966, 339, "buildx → DOCR · compose up", 10.5, p, p["ink2"]))
    o.append(text(966, 354, "healthcheck → auto-rollback", 10.5, p, p["ink2"]))
    o.append(text(966, 369, "deploy/<target>/… tag after the fact", 10.5, p, p["ink2"]))
    o.append(f'<rect x="952" y="406" width="266" height="72" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="1.8"/>')
    o.append(text(966, 429, "stands", 13, p, w="bold"))
    o.append(text(966, 447, "statehub · betmanager · studios", 10.5, p, p["ink2"]))
    o.append(text(966, 463, "read the catalog, not the code", 10.5, p, p["ink2"]))
    o.append(arrow([(1085, 386), (1085, 404)], p, width=2))
    o.append(arrow([(1085, 478), (1085, 506)], p, color=p["hot"], marker="h"))
    # LIVE — кислотная плашка
    o.append(f'<rect x="957" y="513" width="266" height="88" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>')
    o.append(f'<rect x="952" y="508" width="266" height="88" fill="{p["acid"]}" stroke="{p["ink"]}" stroke-width="2.4"/>')
    o.append(text(966, 531, "droplet · live", 13.5, p, p["acidink"], w="800"))
    o.append(text(966, 549, "games · statehub · betmanager · studios", 10.5, p, p["acidink"]))
    o.append(text(966, 565, "nginx + oauth2-proxy", 10.5, p, p["acidink"]))
    o.append(text(966, 581, "GitHub-org SSO on internal hosts", 10.5, p, p["acidink"]))
    o.append(text(952, 626, "rollback is a fallback, never the first response", 9.5, p, p["ink3"]))
    o.append("</g>")

    # ── магистральные стрелки между панелями ─────────────────────
    o.append(arrow([(290, 262), (330, 272), (382, 280)], p, color=p["hot"], width=3, marker="h"))
    o.append(edge_label(336, 258, "publishes", p, anchor="middle"))
    o.append(arrow([(290, 600), (330, 640), (410, 674), (700, 690), (950, 634)], p, width=2.2, dash="5 4"))
    o.append(edge_label(660, 708, "platform: merge to main ships the stands", p, anchor="middle"))
    o.append(arrow([(848, 416), (890, 330), (952, 250)], p, color=p["hot"], width=3, marker="h"))
    o.append(edge_label(872, 366, "game: merge to main", p, anchor="end"))
    o.append(arrow([(682, 575), (900, 520), (952, 448)], p, width=2.2, dash="6 5"))
    o.append(edge_label(880, 548, "slug → {module, client}", p, anchor="middle"))

    # подпись
    o.append(text(40, H - 48, "SemVer tags version packages; main ships services — every accepted deploy is marked with a deploy/<target> tag afterwards", 10.5, p, p["ink3"]))
    o.append(text(40, H - 30, "the seal: a test fails the build the moment a money-moving file drifts out of compliance_files; the lab gets compliance_version", 10.5, p, p["ink3"]))
    o.append("</svg>")
    return "\n".join(o)


DEFAULT_OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
(out / "platform-dark.svg").write_text(build(DARK, "dark"), encoding="utf-8")
(out / "platform-light.svg").write_text(build(LIGHT, "light"), encoding="utf-8")
print("ok:", out / "platform-dark.svg", out / "platform-light.svg")
