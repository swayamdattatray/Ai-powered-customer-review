"""
Review Clustering and Similarity Analysis Tool.
Groups reviews with high lexical and semantic similarity using TF-IDF and Cosine Similarity.
Identifies potential copy-paste, template-driven, or repetitive review campaigns.
"""

import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tools.preprocessor import ReviewPreprocessor

logger = logging.getLogger(__name__)


class ReviewClusterer:
    """Tool for grouping similar reviews into review clusters."""

    def __init__(self, similarity_threshold: float = 0.65):
        self.similarity_threshold = similarity_threshold

    def find_clusters(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects clusters of near-duplicate or suspiciously similar reviews.

        Args:
            reviews: List of review dictionaries containing 'review_text'.

        Returns:
            List of detected cluster dicts:
            [
                {
                    "cluster_id": int,
                    "size": int,
                    "average_similarity": int (percent),
                    "common_source": str,
                    "representative_snippet": str,
                    "status": "Potentially Suspicious Cluster" | "Similar Reviews",
                    "member_reviews": List[Dict]
                }
            ]
        """
        if len(reviews) < 2:
            return []

        cleaned_texts = [ReviewPreprocessor.clean_text(r.get("review_text", "")) for r in reviews]

        # Filter out empty texts
        valid_indices = [i for i, t in enumerate(cleaned_texts) if len(t.split()) >= 2]
        if len(valid_indices) < 2:
            return []

        valid_texts = [cleaned_texts[i] for i in valid_indices]

        try:
            vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(valid_texts)
            sim_matrix = cosine_similarity(tfidf_matrix)

            visited = set()
            clusters = []

            for i in range(len(valid_indices)):
                if i in visited:
                    continue

                cluster_members = [i]
                sim_scores = []

                for j in range(i + 1, len(valid_indices)):
                    if j in visited:
                        continue

                    score = sim_matrix[i, j]
                    if score >= self.similarity_threshold:
                        cluster_members.append(j)
                        sim_scores.append(score)

                # Only consider clusters with 2 or more reviews
                if len(cluster_members) >= 2:
                    for m in cluster_members:
                        visited.add(m)

                    orig_reviews = [reviews[valid_indices[m]] for m in cluster_members]
                    sources = [r.get("source", "Unknown") for r in orig_reviews]
                    common_source = max(set(sources), key=sources.count)

                    avg_sim = round((sum(sim_scores) / len(sim_scores)) * 100) if sim_scores else 95
                    snippet = orig_reviews[0].get("review_text", "")[:120] + "..."

                    clusters.append({
                        "cluster_id": len(clusters) + 1,
                        "size": len(cluster_members),
                        "average_similarity": avg_sim,
                        "common_source": common_source,
                        "representative_snippet": snippet,
                        "status": "Potentially Suspicious Cluster" if avg_sim >= 85 else "Similar Opinion Cluster",
                        "member_reviews": orig_reviews
                    })

            # Sort clusters by size
            clusters.sort(key=lambda c: c["size"], reverse=True)
            return clusters

        except Exception as err:
            logger.error(f"[ReviewClusterer] Error computing similarity clusters: {err}")
            return []
