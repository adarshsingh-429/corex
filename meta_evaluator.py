import json, re, time, os, ssl
from urllib.request import urlopen, Request
from urllib.parse import quote_plus

def fetch_url(url, timeout=10):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except:
        return None

def fetch_json(url, timeout=10):
    content = fetch_url(url, timeout)
    if content:
        try:
            return json.loads(content)
        except:
            return None
    return None

class LiveWebSearch:
    def wikipedia_search(self, query):
        url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + quote_plus(query) + "&format=json&srlimit=3&origin=*"
        data = fetch_json(url)
        facts = []
        if data and "query" in data:
            for result in data["query"].get("search", [])[:2]:
                title = result.get("title", "")
                snippet = re.sub(r"<.*?>", "", result.get("snippet", ""))
                if snippet:
                    facts.append("[Wikipedia] " + title + ": " + snippet)
                extract_url = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles=" + quote_plus(title) + "&explaintext=true&exsentences=5&format=json&origin=*"
                extract_data = fetch_json(extract_url)
                if extract_data and "query" in extract_data:
                    for page in extract_data["query"].get("pages", {}).values():
                        extract = page.get("extract", "")
                        if extract:
                            sentences = re.split(r"(?<=[.!?])\s+", extract)
                            for sent in sentences[:3]:
                                if len(sent) > 20:
                                    facts.append("[Wikipedia] " + sent.strip())
        return facts

    def duckduckgo_search(self, query):
        url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
        html = fetch_url(url)
        facts = []
        if html:
            snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
            for snippet in snippets[:5]:
                clean = re.sub(r"<.*?>", "", snippet).strip()
                if clean and len(clean) > 15:
                    facts.append("[Web] " + clean)
        return facts

    def get_all_facts(self, query):
        facts = []
        facts.extend(self.wikipedia_search(query))
        facts.extend(self.duckduckgo_search(query))
        seen = set()
        unique = []
        for f in facts:
            key = f.lower()[:80]
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique[:15]

class MetaEvaluator:
    def __init__(self):
        self.web_search = LiveWebSearch()

    def evaluate_and_correct(self, question, user_response=None):
        start_time = time.time()
        facts = self.web_search.get_all_facts(question)
        target_response = user_response if user_response else "No response provided."
        evaluation = self._evaluate_response(question, target_response, facts)
        corrected = self._generate_corrected_answer(question, target_response, facts, evaluation)
        return {
            "question": question,
            "original_response": target_response,
            "source": "User" if user_response else "None",
            "reference_facts": facts[:10],
            "ai_responses": {},
            "evaluation": evaluation,
            "corrected_answer": corrected,
            "processing_time": time.time() - start_time,
            "meta_ai_powered": True
        }

    def _evaluate_response(self, question, response, facts):
        resp_dates = set(re.findall(r"\b(1[4-9]\d{2}|20\d{2})\b", response))
        fact_dates = set()
        for fact in facts:
            fact_dates.update(re.findall(r"\b(1[4-9]\d{2}|20\d{2})\b", fact))
        wrong_dates = resp_dates - fact_dates if fact_dates else set()
        correct_dates = resp_dates & fact_dates if fact_dates else set()
        fact_text = " ".join(facts).lower()
        resp_words = set(response.lower().split())
        fact_keywords = set(re.findall(r"\b\w{6,}\b", fact_text))
        matched = len(fact_keywords & resp_words) / max(len(fact_keywords), 1) if fact_keywords else 0

        accuracy = 5.0
        if wrong_dates:
            accuracy -= len(wrong_dates) * 0.8
        if not correct_dates and resp_dates and fact_dates:
            accuracy -= 1.0
        if matched < 0.2 and facts:
            accuracy -= 1.5
        accuracy = max(1.0, min(5.0, accuracy))

        relevance = 5.0
        q_terms = set(re.findall(r"\b\w{4,}\b", question.lower()))
        r_terms = set(re.findall(r"\b\w{4,}\b", response.lower()))
        overlap = len(q_terms & r_terms) / max(len(q_terms), 1)
        if overlap < 0.3:
            relevance -= 2.0
        elif overlap < 0.5:
            relevance -= 0.5
        relevance = max(1.0, min(5.0, relevance))

        hallucination = 5.0
        if wrong_dates:
            hallucination -= 1.5
        if matched < 0.1 and facts:
            hallucination -= 1.5
        absolutes = ["definitely", "certainly", "always", "never"]
        if any(a in response.lower() for a in absolutes):
            hallucination -= 0.5
        hallucination = max(1.0, min(5.0, hallucination))

        completeness = 5.0
        if matched < 0.3:
            completeness -= 1.5
        if len(response.split()) < 20:
            completeness -= 1.0
        completeness = max(1.0, min(5.0, completeness))

        overall = round((relevance * 0.25 + accuracy * 0.30 + hallucination * 0.25 + completeness * 0.20) * 100) / 100

        return {
            "overall_score": overall,
            "relevance": round(relevance, 1),
            "accuracy": round(accuracy, 1),
            "hallucination": round(hallucination, 1),
            "completeness": round(completeness, 1),
            "wrong_dates": list(wrong_dates),
            "correct_dates": list(correct_dates),
            "fact_coverage": round(matched * 100, 1),
            "facts_found": len(facts)
        }

    def _generate_corrected_answer(self, question, original, facts, evaluation):
        if evaluation["overall_score"] >= 4.0:
            return original
        corrected = "Based on verified sources (Wikipedia, live web search):\n\n"
        for fact in facts[:5]:
            clean = re.sub(r"\[.*?\]\s*", "", fact).strip()
            if len(clean) > 20:
                corrected += "* " + clean + "\n"
        corrected += "\n[Note: Original scored " + str(evaluation["overall_score"]) + "/5.0]"
        return corrected
