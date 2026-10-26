import os
import asyncio, subprocess, time
from playwright.async_api import async_playwright

async def main():
    srv = subprocess.Popen(["python3", "-m", "http.server", "8765", "--bind", "127.0.0.1"], cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent / "docs"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
            ctx = await b.new_context(viewport={"width": 390, "height": 844})
            page = await ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            await page.goto("http://localhost:8765/")
            await page.wait_for_timeout(1500)
            # slider at Dec 28 1:48 pm MST = 20:48Z -> minutes from Dec 27 01:00Z
            for label, iso in (("Land's End southbound", "2026-12-28T20:48:00Z"), ("Tropic south", "2026-12-28T16:48:00Z"), ("In PV", "2026-12-29T18:00:00Z"), ("Ojo Jan1", "2027-01-01T18:26:00Z"), ("NYE midnight", "2027-01-01T07:00:00Z")):
                mins = await page.evaluate(f"(Date.parse('{iso}') - Date.parse('2026-12-27T01:00:00Z'))/60000")
                await page.evaluate(f"const r=document.getElementById('voyage'); r.value={int(mins)}; r.dispatchEvent(new Event('input'))")
                txt = await page.evaluate("['rTime','rStatus','rSailed','rSpeed','rNear'].map(i=>document.getElementById(i).textContent).join(' | ')")
                print(label, '->', txt)
            # power at 22.2 and 0
            for v in ("22.2", "0", "11.5"):
                await page.evaluate(f"const s=document.getElementById('spd'); s.value={v}; s.dispatchEvent(new Event('input'))")
                g = await page.evaluate("['gTotal','gEng','gFuel','gGpm','gPmpg','gLeg'].map(i=>document.getElementById(i).textContent).join(' | ')")
                print('speed', v, '->', g)
            # packing persistence
            await page.evaluate("location.hash='#pack'")
            await page.check("#pk0-0")
            await page.check("#pk2-0")
            await page.reload(); await page.wait_for_timeout(800)
            print('pack after reload:', await page.text_content('#packCount'))
            # quiz click
            await page.evaluate("location.hash='#play'")
            await page.click("#qOpts .opt >> nth=0")
            print('quiz:', await page.text_content('#qEx'))
            # offline reload
            await page.wait_for_timeout(2500)
            sw = await page.evaluate("navigator.serviceWorker.controller ? 'controlled' : 'not controlled'")
            print('service worker:', sw)
            await ctx.set_offline(True)
            await page.reload(); await page.wait_for_timeout(800)
            print('offline title:', await page.title(), '| h1:', await page.text_content('#trip h1'))
            print('errors:', errs)
            await b.close()
    finally:
        srv.terminate()

asyncio.run(main())
