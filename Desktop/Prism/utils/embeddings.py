
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

model = SentenceTransformer('all-MiniLM-L6-v2')

def tfidf_similarity(text1: str, text2: str) -> float:
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score), 3)
    except:
        return 0.0


def is_short_jd(text: str) -> bool:
    return len(text.split()) < 50


def keyword_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return round(len(intersection) / len(union), 3)

def calculate_similarities(original_jd: str, other_jds: list[str]) -> list[float]:
    original_embedding = model.encode(original_jd)
    scores = []

    for other in other_jds:
        if is_short_jd(original_jd) or is_short_jd(other):
            score = keyword_similarity(original_jd, other)
        else:
            # Sentence transformer score — semantic meaning
            other_embedding = model.encode(other)
            embedding_score = cosine_similarity(
                [original_embedding], [other_embedding]
            )[0][0]

            # TF-IDF score — keyword level changes
            tfidf_score = tfidf_similarity(original_jd, other)

            # Combined — 60% semantic, 40% keyword
            score = (float(embedding_score) * 0.6) + (tfidf_score * 0.4)

        scores.append(round(float(score), 3))

    return scores

