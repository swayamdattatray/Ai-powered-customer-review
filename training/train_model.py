import sqlite3
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score
)

from preprocessing.text_preprocessor import clean_text


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_NAME = "customer_reviews.db"

MODEL_PATH = "models/sentiment_model.pkl"

VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"


# ============================================================
# LOAD REVIEWS FROM DATABASE
# ============================================================

def load_reviews():

    connection = sqlite3.connect(DATABASE_NAME)

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
# TRAIN AND COMPARE MODELS
# ============================================================

def train_model():

    print("\n============================================")
    print("     AI CUSTOMER REVIEW INTELLIGENCE")
    print("          ML MODEL COMPARISON")
    print("============================================")

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    data = load_reviews()

    if len(data) < 10:

        print("\nNot enough reviews for ML training.")

        print(
            "Please collect at least 10 labelled reviews first."
        )

        return

    print(
        f"\nTotal reviews available: {len(data)}"
    )

    # --------------------------------------------------------
    # PREPARE TEXT AND SENTIMENT
    # --------------------------------------------------------

    reviews = []
    sentiments = []

    for review_text, sentiment in data:

        cleaned_review = clean_text(review_text)

        if cleaned_review.strip():

            reviews.append(cleaned_review)

            sentiments.append(
                str(sentiment).lower()
            )

    print(
        f"Usable reviews: {len(reviews)}"
    )

    # --------------------------------------------------------
    # CHECK SENTIMENT CLASSES
    # --------------------------------------------------------

    unique_sentiments = set(sentiments)

    print("\nSentiment classes found:")

    for sentiment in sorted(unique_sentiments):

        print(
            f" - {sentiment}"
        )

    if len(unique_sentiments) < 2:

        print(
            "\nERROR: At least two sentiment classes "
            "are required for ML training."
        )

        return

    # --------------------------------------------------------
    # TRAIN / TEST SPLIT
    # --------------------------------------------------------

    try:

        reviews_train, reviews_test, y_train, y_test = (
            train_test_split(
                reviews,
                sentiments,
                test_size=0.20,
                random_state=42,
                stratify=sentiments
            )
        )

    except ValueError as error:

        print(
            "\nCould not create a stratified train/test split."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "\nPlease collect more reviews for each "
            "sentiment category."
        )

        return

    # --------------------------------------------------------
    # TF-IDF VECTORIZATION
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        max_features=5000
    )

    # Fit only on training data
    X_train = vectorizer.fit_transform(
        reviews_train
    )

    X_test = vectorizer.transform(
        reviews_test
    )

    # ========================================================
    # CREATE MACHINE LEARNING MODELS
    # ========================================================

    models = {

        "Logistic Regression":
            LogisticRegression(
                max_iter=1000
            ),

        "Multinomial Naive Bayes":
            MultinomialNB(),

        "Linear SVM":
            LinearSVC()
    }

    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    results = {}

    print("\n============================================")
    print("             MODEL COMPARISON")
    print("============================================")

    for model_name, model in models.items():

        print(
            f"\nTraining {model_name}..."
        )

        # ----------------------------------------------------
        # TRAIN MODEL
        # ----------------------------------------------------

        model.fit(
            X_train,
            y_train
        )

        # ----------------------------------------------------
        # PREDICT
        # ----------------------------------------------------

        predictions = model.predict(
            X_test
        )

        # ----------------------------------------------------
        # ACCURACY
        # ----------------------------------------------------

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        # ----------------------------------------------------
        # F1 SCORE
        # ----------------------------------------------------

        weighted_f1 = f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )

        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        results[model_name] = {

            "model": model,

            "accuracy": accuracy,

            "f1_score": weighted_f1
        }

        # ----------------------------------------------------
        # DISPLAY RESULTS
        # ----------------------------------------------------

        print(
            f"\n{model_name}"
        )

        print(
            f"Accuracy : {accuracy * 100:.2f}%"
        )

        print(
            f"F1 Score : {weighted_f1:.4f}"
        )

        print(
            "\nClassification Report:"
        )

        print(
            classification_report(
                y_test,
                predictions,
                zero_division=0
            )
        )

    # ========================================================
    # SELECT BEST MODEL
    # ========================================================

    best_model_name = max(
        results,
        key=lambda name: results[name]["f1_score"]
    )

    best_model = results[
        best_model_name
    ]["model"]

    best_accuracy = results[
        best_model_name
    ]["accuracy"]

    best_f1 = results[
        best_model_name
    ]["f1_score"]

    # ========================================================
    # FINAL MODEL COMPARISON
    # ========================================================

    print("\n============================================")
    print("          FINAL MODEL COMPARISON")
    print("============================================")

    print(
        "\nModel                     Accuracy       F1 Score"
    )

    print(
        "----------------------------------------------------"
    )

    for model_name, result in results.items():

        print(
            f"{model_name:<25}"
            f"{result['accuracy'] * 100:>8.2f}%"
            f"{result['f1_score']:>16.4f}"
        )

    # ========================================================
    # BEST MODEL
    # ========================================================

    print("\n============================================")

    print(
        f"BEST MODEL: {best_model_name}"
    )

    print(
        f"Best Accuracy: {best_accuracy * 100:.2f}%"
    )

    print(
        f"Best F1 Score: {best_f1:.4f}"
    )

    print(
        "============================================"
    )

    # ========================================================
    # SAVE BEST MODEL
    # ========================================================

    joblib.dump(
        best_model,
        MODEL_PATH
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH
    )

    print("\nBest model saved successfully!")

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Vectorizer: {VECTORIZER_PATH}"
    )

    print("\n============================================")

    print(
        "       MODEL TRAINING COMPLETED"
    )

    print(
        "============================================")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    train_model()