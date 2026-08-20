import re


def analyze_aspects(review_text):

    text = review_text.lower()

    aspects = {}

    keywords = {
        "camera": ["camera", "photo", "picture"],
        "battery": ["battery", "charging", "charge"],
        "performance": ["performance", "speed", "fast", "slow"],
        "quality": ["quality", "build", "material"],
        "price": ["price", "cost", "expensive", "cheap"],
        "delivery": ["delivery", "shipping", "arrived"],
        "display": ["display", "screen"],
        "sound": ["sound", "speaker", "audio"]
    }

    positive_words = [
        "good",
        "great",
        "excellent",
        "amazing",
        "best",
        "nice",
        "fast",
        "very good",
        "awesome",
        "fantastic",
        "perfect"
    ]

    negative_words = [
        "bad",
        "poor",
        "worst",
        "slow",
        "terrible",
        "expensive",
        "problem",
        "horrible",
        "disappointing",
        "weak"
    ]

    # Check each aspect
    for aspect, words in keywords.items():

        for word in words:

            match = re.search(
                r"\b" + re.escape(word) + r"\b",
                text
            )

            if match:

                # Get only a small local context around the aspect
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)

                context = text[start:end]

                # Check sentiment words near the aspect
                positive_found = any(
                    re.search(r"\b" + re.escape(p) + r"\b", context)
                    for p in positive_words
                )

                negative_found = any(
                    re.search(r"\b" + re.escape(n) + r"\b", context)
                    for n in negative_words
                )

                # Determine sentiment
                if positive_found and not negative_found:
                    sentiment = "Positive"

                elif negative_found and not positive_found:
                    sentiment = "Negative"

                else:
                    # If both are found, use the closest sentiment word
                    sentiment_words = []

                    for p in positive_words:
                        p_match = re.search(
                            r"\b" + re.escape(p) + r"\b",
                            context
                        )

                        if p_match:
                            distance = abs(
                                p_match.start() -
                                (match.start() - start)
                            )
                            sentiment_words.append(
                                (distance, "Positive")
                            )

                    for n in negative_words:
                        n_match = re.search(
                            r"\b" + re.escape(n) + r"\b",
                            context
                        )

                        if n_match:
                            distance = abs(
                                n_match.start() -
                                (match.start() - start)
                            )
                            sentiment_words.append(
                                (distance, "Negative")
                            )

                    if sentiment_words:
                        sentiment = min(
                            sentiment_words,
                            key=lambda x: x[0]
                        )[1]
                    else:
                        sentiment = "Neutral"

                aspects[aspect] = sentiment

                break

    return aspects