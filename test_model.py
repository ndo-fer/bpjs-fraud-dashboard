import joblib

model = joblib.load("models/winner_model.joblib")

print("MODEL BERHASIL DILOAD")
print(type(model))

print("\nFEATURES:")
print(model.feature_names_in_)