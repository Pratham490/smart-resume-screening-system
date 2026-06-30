import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def _tf_idf_vectors(documents: list[str]) -> list[dict[str, float]]:
    tokenized_documents = [_tokenize(document) for document in documents]
    doc_freq: Counter[str] = Counter()
    for tokens in tokenized_documents:
        doc_freq.update(set(tokens))

    total_docs = len(tokenized_documents)
    vectors = []
    for tokens in tokenized_documents:
        counts = Counter(tokens)
        vector = {}
        for token, count in counts.items():
            tf = count / max(1, len(tokens))
            idf = math.log((1 + total_docs) / (1 + doc_freq[token])) + 1.0
            vector[token] = tf * idf
        vectors.append(vector)
    return vectors


def _cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    if not vec1 or not vec2:
        return 0.0

    shared_terms = set(vec1) & set(vec2)
    numerator = sum(vec1[term] * vec2[term] for term in shared_terms)
    denominator = math.sqrt(sum(value * value for value in vec1.values())) * math.sqrt(sum(value * value for value in vec2.values()))

    if denominator == 0:
        return 0.0

    return numerator / denominator


def calculateskillmatch(resumeskills: list[str], requiredskills: list[str]) -> dict:
    resumeskillslower = {skill.lower() for skill in resumeskills}
    requiredskillslower = {skill.lower() for skill in requiredskills}

    matched = resumeskillslower & requiredskillslower
    missing = requiredskillslower - resumeskillslower

    if requiredskillslower:
        skillscore = (len(matched) / len(requiredskillslower)) * 100
    else:
        skillscore = 0.0

    return {
        "matched": [skill for skill in requiredskills if skill.lower() in matched],
        "missing": [skill for skill in requiredskills if skill.lower() in missing],
        "skillscore": skillscore,
    }


def calculatetextsimilarity(resumetext: str, jdtext: str) -> float:
    if not resumetext.strip() or not jdtext.strip():
        return 0.0

    vectors = _tf_idf_vectors([resumetext, jdtext])
    similarity = _cosine_similarity(vectors[0], vectors[1])
    return similarity * 100.0


def generateexplanation(skillscore: float, textscore: float, matchedskills: list[str], missingskills: list[str], finalscore: int) -> str:
    if finalscore >= 80:
        strength = "Strong match"
    elif finalscore >= 60:
        strength = "Good match"
    elif finalscore >= 40:
        strength = "Moderate match"
    else:
        strength = "Weak match"

    lines = [f"{strength} with {finalscore}% relevance score."]

    if matchedskills:
        topmatches = matchedskills[:3]
        lines.append(f"Key matching skills: {', '.join(topmatches)}.")

    if missingskills:
        topmissing = missingskills[:2]
        lines.append(f"Consider adding: {', '.join(topmissing)}.")

    return " ".join(lines)


def matchresumetojd(resumetext: str, resumeskills: list[str], jdtext: str, requiredskills: list[str]) -> dict:
    skillresult = calculateskillmatch(resumeskills, requiredskills)
    textscore = calculatetextsimilarity(resumetext, jdtext)

    finalscore = int((skillresult["skillscore"] * 0.6) + (textscore * 0.4))
    finalscore = min(100, max(0, finalscore))

    explanation = generateexplanation(
        skillresult["skillscore"],
        textscore,
        skillresult["matched"],
        skillresult["missing"],
        finalscore,
    )

    return {
        "matchscore": finalscore,
        "matchedskills": skillresult["matched"],
        "missingskills": skillresult["missing"],
        "explanation": explanation,
    }
