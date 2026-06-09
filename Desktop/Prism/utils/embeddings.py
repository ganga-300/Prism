
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarities(original_jd: str, other_jds: list[str]) -> list[float]:
    # Step 1 — encode original
    original_embedding = model.encode(original_jd)
    
    scores = []
    
    # Step 2 — encode each other JD and compare
    for other in other_jds:
        other_embedding = model.encode(other)
        
        # Step 3 — calculate similarity
        score = cosine_similarity([original_embedding], [other_embedding])[0][0]
        scores.append(round(float(score), 3))
    
    # Step 4 — return all scores
    return scores