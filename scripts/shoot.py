import os
import asyncio, sys, os
from playwright.async_api import async_playwright

import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "dist" / "Koningsdam-Voyage-Guide.html").as_uri()
OUT = str(ROOT / "preview" / "shots")
os.makedirs(OUT, exist_ok=True)

TARGETS = sys.argv[1:] or ["trip"]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        for scheme in ("light", "dark"):
            ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme)
            page = await ctx.new_page()
            errs = []
            page.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
            await page.goto(SRC)
            await page.wait_for_timeout(400)
            for t in TARGETS:
                view, _, sel = t.partition("@")
                await page.evaluate(f"location.hash='#{view}'")
                await page.wait_for_timeout(300)
                ov = await page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
                if ov[0] > ov[1]:
                    wide = await page.evaluate("""() => { const w = document.documentElement.clientWidth; return [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > w + 1 && r.width > 0 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 6).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().right)); }""")
                    print(scheme, t, "OVERFLOW", ov, wide)
                name = t.replace("@", "_").replace("#", "").replace(" ", "").replace(".", "")
                if sel:
                    el = await page.query_selector(sel)
                    if el:
                        await el.scroll_into_view_if_needed()
                        await el.screenshot(path=f"{OUT}/{scheme}_{name}.png")
                    else:
                        print("missing", sel)
                else:
                    await page.screenshot(path=f"{OUT}/{scheme}_{name}.png")
            if errs:
                print(scheme, "console:", errs[:10])
            await ctx.close()
            if "--light-only" in sys.argv:
                break
        await b.close()

asyncio.run(main())
