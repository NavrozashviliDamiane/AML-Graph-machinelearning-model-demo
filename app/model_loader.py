import joblib
import os

model_path = "models/aml_model.pkl"

if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"Model file not found at {model_path}. "
        "Please train the model first by running:\n"
        "  1. python ml/export_features.py\n"
        "  2. python ml/build_dataset.py\n"
        "  3. python ml/train_model.py"
    )

model = joblib.load(model_path)
