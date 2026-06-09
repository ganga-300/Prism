
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')


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
    # Step 1 — encode original
    original_embedding = model.encode(original_jd)
    
    scores = []
    
    # Step 2 — encode each other JD and compare
    for other in other_jds:
    
        if is_short_jd(original_jd) or is_short_jd(other):
            score = keyword_similarity(original_jd, other)
        else:
            other_embedding = model.encode(other)
            score = cosine_similarity([original_embedding], [other_embedding])[0][0]
        
        scores.append(round(float(score), 3))
    
    # Step 4 — return all scores
    return scores


