import os, json, requests

def summarize_with_gemini(context_type: str, source: str, title: str, text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        snippet = (text or title or "")[:400]
        return {
            "ExecutiveSummary": snippet,
            "BusinessInsight": "Potentially relevant; manual review recommended.",
            "RelevanceScore": 50,
            "CanonicalLink": ""
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = "\n".join([
        "You are an analyst for busy product leaders.",
        "Return a JSON object with keys EXACTLY: ExecutiveSummary, BusinessInsight, RelevanceScore, CanonicalLink.",
        "ExecutiveSummary: 3-5 sentences. BusinessInsight: 1-2 sentences (why it matters).",
        "RelevanceScore: integer 0-100 using rubric: 80-100 primary/launch/regulatory-impact; 50-79 secondary; <50 marginal.",
        f"Context Type={context_type}; Source={source}; Title=\"{title}\".",
        "Text:",
        (text or title)[:6000]
    ])
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512}
    }
    try:
        res = requests.post(url, json=payload, timeout=45)
        res.raise_for_status()
        data = res.json()
        txt = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text","")
        txt = txt.replace("```json","").replace("```","").strip()
        obj = json.loads(txt)
        return {
            "ExecutiveSummary": obj.get("ExecutiveSummary",""),
            "BusinessInsight": obj.get("BusinessInsight",""),
            "RelevanceScore": int(obj.get("RelevanceScore", 0)) if str(obj.get("RelevanceScore","")).isdigit() else 0,
            "CanonicalLink": obj.get("CanonicalLink","")
        }
    except Exception:
        snippet = (text or title or "")[:400]
        return {
            "ExecutiveSummary": snippet,
            "BusinessInsight": "Potentially relevant; manual review recommended.",
            "RelevanceScore": 50,
            "CanonicalLink": ""
        }
