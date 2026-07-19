"""
Runs two studies for the thesis WITHOUT touching your real trained model:

  1. Train/test split comparison  (60/40, 70/30, 80/20, 90/10)
  2. Grid search over hyperparameters (layer sizes, dropout, learning rate, batch size)
"""
import os
import glob
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras

GREEN = "#27ae60"
DARK  = "#1a7a0a"

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "training_data")
OUT_DIR  = os.path.join(HERE, "experiments")
os.makedirs(OUT_DIR, exist_ok=True)

# Fixed seed so the whole study is reproducible
SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)


# ── Load data
def load_data():
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        raise FileNotFoundError(
            "No CSV files found in ai/training_data/. Record data first."
        )
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    X = df.drop("label", axis=1).values.astype(np.float32)
    y = df["label"].values
    enc = LabelEncoder()
    y_enc = enc.fit_transform(y)
    print(f"Loaded {len(df)} frames, classes: {list(enc.classes_)}")
    return X, y_enc, len(enc.classes_)


# ── Build a model with given hyperparameters
def build_model(input_dim, n_classes, layers, dropout, lr):
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(input_dim,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation="relu"))
        if dropout > 0:
            model.add(keras.layers.Dropout(dropout))
    model.add(keras.layers.Dense(n_classes, activation="softmax"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── EXPERIMENT 1: train/test split comparison
def experiment_splits(X, y, n_classes):
    print("\n=== Experiment 1: train/test split comparison ===")
    test_sizes = [0.40, 0.30, 0.20, 0.10]   # 60/40, 70/30, 80/20, 90/10
    rows = []

    for ts in test_sizes:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=ts, random_state=SEED, stratify=y
        )
        model = build_model(X.shape[1], n_classes,
                            layers=[256, 128, 64], dropout=0.3, lr=1e-3)
        es = keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
        model.fit(X_tr, y_tr, validation_data=(X_te, y_te),
                  epochs=50, batch_size=32, verbose=0, callbacks=[es])
        _, acc = model.evaluate(X_te, y_te, verbose=0)
        train_pct = int(round((1 - ts) * 100))
        test_pct  = int(round(ts * 100))
        label = f"{train_pct}/{test_pct}"
        rows.append({"split": label, "train_pct": train_pct,
                     "test_accuracy": acc})
        print(f"  Split {label}: test accuracy = {acc:.4f}")

    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT_DIR, "split_comparison.csv"), index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(res["train_pct"], res["test_accuracy"],
            marker="o", color=GREEN, linewidth=2)
    for _, r in res.iterrows():
        ax.annotate(f"{r['test_accuracy']:.3f}",
                    (r["train_pct"], r["test_accuracy"]),
                    textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=9)
    ax.set_xlabel("Training data percentage (%)")
    ax.set_ylabel("Test accuracy")
    ax.set_title("Test Accuracy vs. Train/Test Split")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "split_comparison.png"),
                dpi=200, bbox_inches="tight")
    plt.close()
    print("  Saved split_comparison.png and split_comparison.csv")


# ── EXPERIMENT 2: grid search
def experiment_grid(X, y, n_classes):
    print("\n=== Experiment 2: grid search ===")
    # Fixed 80/20 split for all grid-search runs
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    # Hyperparameter grid
    grid_layers   = [[128, 64], [256, 128, 64], [512, 256, 128]]
    grid_dropout  = [0.2, 0.3, 0.5]
    grid_lr       = [1e-3, 5e-4]
    grid_batch    = [16, 32]

    combos = list(itertools.product(grid_layers, grid_dropout,
                                    grid_lr, grid_batch))
    print(f"  Testing {len(combos)} configurations...")

    rows = []
    for i, (layers, dropout, lr, batch) in enumerate(combos, 1):
        model = build_model(X.shape[1], n_classes, layers, dropout, lr)
        es = keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
        hist = model.fit(X_tr, y_tr, validation_data=(X_te, y_te),
                         epochs=50, batch_size=batch, verbose=0,
                         callbacks=[es])
        _, acc = model.evaluate(X_te, y_te, verbose=0)
        rows.append({
            "layers": "-".join(map(str, layers)),
            "dropout": dropout,
            "learning_rate": lr,
            "batch_size": batch,
            "test_accuracy": acc,
        })
        print(f"  [{i}/{len(combos)}] layers={layers} dropout={dropout} "
              f"lr={lr} batch={batch} -> acc={acc:.4f}")

    res = pd.DataFrame(rows).sort_values("test_accuracy", ascending=False)
    res.to_csv(os.path.join(OUT_DIR, "grid_search_results.csv"), index=False)
    res.head(10).to_csv(os.path.join(OUT_DIR, "grid_search_top.csv"), index=False)

    print("\n  Top 5 configurations:")
    print(res.head(5).to_string(index=False))
    print("\n  Saved grid_search_results.csv and grid_search_top.csv")


if __name__ == "__main__":
    X, y, n_classes = load_data()
    experiment_splits(X, y, n_classes)
    experiment_grid(X, y, n_classes)
    print("\nAll experiments complete. Results are in ai/experiments/")
