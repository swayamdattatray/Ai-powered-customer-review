import sqlite3
import joblib

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from preprocessing.text_preprocessor import clean_text


DATABASE_NAME = "customer_reviews.db"

MODEL_PATH = "models/sentiment_model.pkl"

VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"


# ============================================================
# LOAD REVIEWS FROM DATABASE
# ============================================================

def load_reviews():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT review_text, sentiment
        FROM reviews
        WHERE review_text IS NOT NULL
        AND sentiment IS NOT NULL
    """)

    data = cursor.fetchall()

    connection.close()

    return data


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model():

    print("\n========================================")
    print("   SENTIMENT MODEL EVALUATION")
    print("========================================")


    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    print("\nLoading trained model...")

    model = joblib.load(
        MODEL_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    print("Model loaded successfully.")


    # --------------------------------------------------------
    # LOAD DATABASE DATA
    # --------------------------------------------------------

    data = load_reviews()


    if len(data) == 0:

        print("\nNo labelled reviews found.")
        print("Please add reviews to the database first.")

        return


    print(
        f"\nTotal labelled reviews: {len(data)}"
    )


    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    reviews = []

    actual_sentiments = []


    for review_text, sentiment in data:

        cleaned = clean_text(
            review_text
        )

        reviews.append(
            cleaned
        )

        actual_sentiments.append(
            str(sentiment).lower()
        )


    # --------------------------------------------------------
    # CONVERT TEXT TO TF-IDF
    # --------------------------------------------------------

    X = vectorizer.transform(
        reviews
    )


    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    predictions = model.predict(
        X
    )


    predictions = [
        str(prediction).lower()
        for prediction in predictions
    ]


    # ========================================================
    # ACCURACY
    # ========================================================

    accuracy = accuracy_score(
        actual_sentiments,
        predictions
    )


    print("\n========================================")
    print("MODEL ACCURACY")
    print("========================================")

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )


    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    print("\n========================================")
    print("CLASSIFICATION REPORT")
    print("========================================")

    print(
        classification_report(
            actual_sentiments,
            predictions,
            zero_division=0
        )
    )


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print("\n========================================")
    print("CONFUSION MATRIX")
    print("========================================")

    labels = [
        "negative",
        "neutral",
        "positive"
    ]

    matrix = confusion_matrix(
        actual_sentiments,
        predictions,
        labels=labels
    )

    print(
        "                 Predicted"
    )

    print(
        "              Negative Neutral Positive"
    )

    print(
        f"Actual Negative   {matrix[0][0]:<7} "
        f"{matrix[0][1]:<7} "
        f"{matrix[0][2]}"
    )

    print(
        f"Actual Neutral    {matrix[1][0]:<7} "
        f"{matrix[1][1]:<7} "
        f"{matrix[1][2]}"
    )

    print(
        f"Actual Positive   {matrix[2][0]:<7} "
        f"{matrix[2][1]:<7} "
        f"{matrix[2][2]}"
    )


    # ========================================================
    # FINISHED
    # ========================================================

    print("\n========================================")
    print("EVALUATION COMPLETED SUCCESSFULLY")
    print("========================================")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate_model()