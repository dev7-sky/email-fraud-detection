import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

print("Loading dataset...")
df = pd.read_csv('data/Phishing_Email.csv', index_col=0)
df = df.dropna(subset=['Email Text', 'Email Type'])

X = df['Email Text'].astype(str)
y = df['Email Type'].astype(str)

# Train-test split for evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training model...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Evaluate model (Precision, Recall report)
y_pred = model.predict(X_test_vec)
print("\n--- Model Evaluation Metrics ---")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Model and vectorizer saved successfully!")