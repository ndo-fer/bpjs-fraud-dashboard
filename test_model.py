from utils.scoring import load_artifacts

artifacts = load_artifacts()
info = artifacts["winner_info"]

print("ARTIFACT BERHASIL DILOAD")
print(type(artifacts["clf"]))
print(info["winner_features"])
