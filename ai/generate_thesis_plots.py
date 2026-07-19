import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report, precision_recall_fscore_support
import tensorflow as tf

GREEN = "#27ae60"
DARK  = "#1a7a0a"
MID   = "#52c41a"

HERE         = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(HERE, "training_data")
MODEL_PATH   = os.path.join(HERE, "exercise_model.keras")
LABELS_PATH  = os.path.join(HERE, "label_classes.npy")
HISTORY_PATH = os.path.join(HERE, "training_history.npy")

DISPLAY = {"pushup": "Push-up", "squat": "Squat", "bicep_curl": "Bicep Curl"}


def load_data():
    all_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
    return df


# -- 1. DATASET DISTRIBUTION
def make_dataset_distribution(df):
    counts = df["label"].value_counts()
    labels = [DISPLAY.get(c, c) for c in counts.index]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, counts.values, color=GREEN, edgecolor=DARK)
    ax.set_ylabel("Number of frames")
    ax.set_title("Training Dataset Distribution")
    ax.grid(True, axis="y", alpha=0.3)

    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, val,
                str(val), ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    out = os.path.join(HERE, "dataset_distribution.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# -- 2. CONFUSION MATRIX
def make_confusion_matrix(df):
    model   = tf.keras.models.load_model(MODEL_PATH)
    classes = np.load(LABELS_PATH, allow_pickle=True)

    X = df.drop("label", axis=1).values.astype(np.float32)
    y = df["label"].values
    encoder = LabelEncoder(); encoder.classes_ = classes
    y_enc = encoder.transform(y)

    _, X_test, _, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    cm = confusion_matrix(y_test, y_pred)
    cm_norm = cm / cm.sum(axis=1, keepdims=True)
    labels = [DISPLAY.get(c, c) for c in classes]

    fig, ax = plt.subplots(figsize=(6, 5.2))
    cmap = LinearSegmentedColormap.from_list("fitgreen", ["#ffffff", GREEN])
    im = ax.imshow(cm_norm, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(labels))); ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels); ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted label"); ax.set_ylabel("True label")
    ax.set_title("Confusion Matrix")

    for i in range(len(labels)):
        for j in range(len(labels)):
            pct = cm_norm[i, j] * 100
            color = "white" if cm_norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{cm[i, j]}\n({pct:.1f}%)",
                    ha="center", va="center", color=color, fontsize=10)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Proportion")
    plt.tight_layout()
    out = os.path.join(HERE, "confusion_matrix.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()

    acc = np.trace(cm) / cm.sum()
    print(f"\n=== Test accuracy: {acc:.1%} ===")
    print(classification_report(y_test, y_pred, target_names=labels))
    print(f"Saved {out}")

    return X_test, y_test, y_pred, classes


# -- 3. PER-CLASS METRICS
def make_per_class_metrics(y_test, y_pred, classes):
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=range(len(classes)))
    labels = [DISPLAY.get(c, c) for c in classes]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(x - width, precision, width, label="Precision", color=GREEN)
    ax.bar(x,         recall,    width, label="Recall",    color=MID)
    ax.bar(x + width, f1,        width, label="F1-score",  color=DARK)

    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Score"); ax.set_ylim(0, 1.05)
    ax.set_title("Per-Class Classification Metrics")
    ax.legend(loc="lower right"); ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(HERE, "per_class_metrics.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# -- 4. TRAINING CURVES
def make_training_curves():
    if not os.path.exists(HISTORY_PATH):
        print("\nNo training_history.npy found - skipping training curves.")
        print("See the comment at the bottom of this file to enable it.")
        return

    hist = np.load(HISTORY_PATH, allow_pickle=True).item()
    epochs = np.arange(1, len(hist["accuracy"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.plot(epochs, hist["accuracy"], color=GREEN, linewidth=2, label="Training accuracy")
    ax1.plot(epochs, hist["val_accuracy"], color=DARK, linewidth=2, linestyle="--", label="Validation accuracy")
    ax1.set_xlabel("Epoch"); ax1.set_ylabel("Accuracy")
    ax1.set_title("Model Accuracy over Epochs")
    ax1.legend(loc="lower right"); ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, hist["loss"], color=GREEN, linewidth=2, label="Training loss")
    ax2.plot(epochs, hist["val_loss"], color=DARK, linewidth=2, linestyle="--", label="Validation loss")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Loss")
    ax2.set_title("Model Loss over Epochs")
    ax2.legend(loc="upper right"); ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(HERE, "training_curves.png")
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    df = load_data()
    make_dataset_distribution(df)
    X_test, y_test, y_pred, classes = make_confusion_matrix(df)
    make_per_class_metrics(y_test, y_pred, classes)
    make_training_curves()


