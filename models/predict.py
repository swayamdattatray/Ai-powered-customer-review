import joblib
from preprocessing.text_preprocessor import clean_text


MODEL_PATH = "models/sentiment_model.pkl"
VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"


model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def predict_sentiment(review):

    cleaned_review = clean_text(review)

    review_vector = vectorizer.transform([cleaned_review])

    prediction = model.predict(review_vector)

    return prediction[0]


if __name__ == "__main__":

    review = input("Enter a customer review: ")

    result = predict_sentiment(review)

    print()
    print("Review:", review)
    print("Predicted Sentiment:", result)