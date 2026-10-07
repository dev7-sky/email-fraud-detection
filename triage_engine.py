import joblib
import os

class MLTriageEngine:
    def __init__(self):
        model_path = 'email_fraud_model.pkl'
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None

    def analyze_email(self, text: str):
        if self.model is None:
            return 50, "Medium Priority (Model missing)"
        
        # Model se probability nikalo (0 to 1)
        probability = self.model.predict_proba([text])[0][1]
        risk_score = int(probability * 100)
        
        if risk_score >= 70:
            level = "High Priority (Critical Threat)"
        elif risk_score >= 40:
            level = "Medium Priority (Investigate)"
        else:
            level = "Low Risk / False Positive"
            
        return risk_score, level