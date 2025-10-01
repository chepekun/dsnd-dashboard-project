import pickle
from pathlib import Path
from typing import Protocol

import numpy.typing as npt

project_root = Path(__file__).parents[1]

model_path = project_root / "assets" / "model.pkl"


class ClassifierModel(Protocol):
    def predict_proba(self, x) -> npt.NDArray: ...


def load_model() -> ClassifierModel:
    with model_path.open("rb") as file:
        model = pickle.load(file)

    if not hasattr(model, "predict_proba"):
        raise Exception("The used model should be a classifier with a 'predict_proba' method.")

    return model
