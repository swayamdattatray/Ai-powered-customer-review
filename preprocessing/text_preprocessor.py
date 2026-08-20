import re


def clean_text(text):
    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-z\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":
    review = "This Product is AMAZING!!! Very good quality :)"

    cleaned_review = clean_text(review)

    print("Original Review:")
    print(review)

    print("\nCleaned Review:")
    print(cleaned_review)