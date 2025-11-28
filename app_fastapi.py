# app_fastapi.py
import os
import re
import time
import base64
import tempfile
import requests
import pandas as pd
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from heuristics import compute_answer_from_context
from pdf_utils import parse_pdf_bytes
from utils.downloader import download_url_or_datauri
from utils.logger import log


API_SECRET = os.getenv("API_SECRET", "change-me")
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "60"))
OVERALL_TIMEOUT = int(os.getenv("OVERALL_TIMEOUT", "150"))

app = FastAPI(title="LLM Analysis Quiz Solver - FastAPI")


class TaskPayload(BaseModel):
    email: str
    secret: str
    url: str


def extract_submit_urls(text: str):
    urls = re.findall(
        r'https?://[^\s"\'<>]+/submit[^\s"\'<>]*',
        text,
        flags=re.I
    )
    return urls


@app.post("/task")
async def task_handler(payload: TaskPayload):
    if payload.secret != API_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    start = time.time()
    url = payload.url
    log(f"[+] Solving: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context()
            page = await ctx.new_page()
            await page.goto(url, wait_until="networkidle", timeout=BROWSER_TIMEOUT * 1000)
            await page.wait_for_timeout(500)

            visible = await page.inner_text("body")
            html = await page.content()

            submit_urls = extract_submit_urls(html + "\n" + visible)

            # Extract all links
            anchors = await page.query_selector_all("a")
            links = []

            for a in anchors:
                try:
                    h = await a.get_attribute("href")
                    if h:
                        links.append(h)
                except:
                    continue

            # inline atob()
            for m in re.finditer(r'atob\(`([^`]+)`\)', html):
                links.append({"atob": m.group(1)})

            # inline data: URIs
            for m in re.finditer(r'(data:[^"\'<>]+)', html):
                links.append(m.group(1))

            # Download and parse
            tables = []
            full_text = visible

            for link in links:
                if time.time() - start > OVERALL_TIMEOUT:
                    break

                b = download_url_or_datauri(link, base_url=url)
                if not b:
                    continue

                # PDF
                if b[:4] == b"%PDF":
                    txt, tbls = parse_pdf_bytes(b)
                    full_text += "\n" + txt
                    tables.extend(tbls)
                    continue

                # CSV or text
                try:
                    if b.count(b",") >= 3:
                        df = pd.read_csv(BytesIO(b))
                        tables.append(df)
                        continue
                except:
                    pass

                try:
                    full_text += "\n" + b.decode("utf8", errors="ignore")
                except:
                    pass

            await browser.close()

    except PWTimeout:
        raise HTTPException(status_code=500, detail="Browser timeout")

    # compute answer
    answer = compute_answer_from_context(full_text, tables)

    if not submit_urls:
        return {
            "ok": False,
            "reason": "No submit URL found",
            "derived_answer": answer,
            "visible_snippet": full_text[:2000]
        }

    submit_url = submit_urls[0]
    submission = {
        "email": payload.email,
        "secret": payload.secret,
        "url": payload.url,
        "answer": answer
    }

    try:
        resp = requests.post(submit_url, json=submission, timeout=30)
        return {
            "ok": True,
            "submit_url": submit_url,
            "submit_status": resp.status_code,
            "submit_response": resp.text[:2000],
            "derived_answer": answer
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "answer": answer
        }
