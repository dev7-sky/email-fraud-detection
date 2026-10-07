import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# 1. Sample Data (Agar tera apna dataset hai toh pd.read_csv('tera_file.csv') use kar lena)
data = {
    'message': [
        "Congratulations you have won a lottery of 1000000 dollars click here",
        "Hey, are we still meeting for lunch tomorrow at 12 PM?",
        "Urgent your bank account is suspended verify password immediately",
        "Please find attached the project report for our meeting",
        "Claim your free gift card now by clicking this link",
        "Hi John, can you review the pull request on GitHub when free?"
    ],
    'label': [0, 1, 0, 1, 0, 1]  # 0 = Fraud/Spam, 1 = Safe/Ham
}
df = pd.DataFrame(data)

X = df['message']
y = df['label']

# 2. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Pipeline (TF-IDF + Logistic Regression)
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression())
])

# 4. Train Model
model_pipeline.fit(X_train, y_train)

# 5. Save Model
joblib.dump(model_pipeline, 'email_fraud_model.pkl')
print("Model trained and saved successfully as email_fraud_model.pkl!")