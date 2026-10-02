"""Create publication-ready figures for the FLORES+ baseline."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(".cache/matplotlib").resolve()),
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SUMMARY_PATH = Path("results/summary/tokenizer_language_summary.csv")
DIACRITICS_PATH = Path("results/summary/diacritics_summary.csv")
FIGURE_DIR = Path("results/figures")
METADATA_PATH = FIGURE_DIR / "figure_metadata.json"

LANGUAGES = ["English", "Hausa", "Igbo", "Yoruba"]
COLORS = {"natlas": "#294C60", "gemma4": "#D56F3E"}
LABELS = {"natlas": "N-ATLaS / Llama 3", "gemma4": "Gemma 4"}


def save_figure(figure: plt.Figure, stem: str) -> list[str]:
    paths = []
    for extension in ("png", "svg"):
        path = FIGURE_DIR / f"{stem}.{extension}"
        figure.savefig(
            path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
        )
        paths.append(str(path))
    plt.close(figure)
    return paths


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "legend.frameon": False,
            "figure.dpi": 140,
        }
    )


def grouped_bars(
    data: pd.DataFrame,
    value_column: str,
    low_column: str,
    high_column: str,
    ylabel: str,
    title: str,
    stem: str,
    reference_line: float | None = None,
) -> list[str]:
    figure, axis = plt.subplots(figsize=(8.2, 4.8))
    positions = np.arange(len(LANGUAGES))
    width = 0.34

    for offset, tokenizer in zip((-width / 2, width / 2), COLORS, strict=True):
        subset = (
            data[data["tokenizer"] == tokenizer]
            .set_index("language")
            .loc[LANGUAGES]
        )
        values = subset[value_column].to_numpy()
        errors = np.vstack(
            [
                values - subset[low_column].to_numpy(),
                subset[high_column].to_numpy() - values,
            ]
        )
        bars = axis.bar(
            positions + offset,
            values,
            width,
            label=LABELS[tokenizer],
            color=COLORS[tokenizer],
            yerr=errors,
            capsize=3,
            error_kw={"elinewidth": 1, "capthick": 1},
        )
        axis.bar_label(bars, fmt="%.2f", padding=3, fontsize=8.5)

    if reference_line is not None:
        axis.axhline(
            reference_line,
            color="#777777",
            linewidth=1,
            linestyle="--",
            zorder=0,
        )
    axis.set_xticks(positions, LANGUAGES)
    axis.set_ylabel(ylabel)
    axis.set_title(title, loc="left", fontweight="bold")
    axis.legend(loc="upper left")
    axis.margins(x=0.04)
    axis.set_ylim(bottom=0)
    figure.tight_layout()
    return save_figure(figure, stem)


def fragmentation_figure(data: pd.DataFrame) -> list[str]:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    fragments = [
        ("share_words_1_token", "1 token", "#2A9D8F"),
        ("share_words_2_tokens", "2 tokens", "#E9C46A"),
        ("share_words_3_tokens", "3 tokens", "#F4A261"),
        ("share_words_4plus_tokens", "4+ tokens", "#C44536"),
    ]

    for axis, tokenizer in zip(axes, COLORS, strict=True):
        subset = (
            data[data["tokenizer"] == tokenizer]
            .set_index("language")
            .loc[LANGUAGES]
        )
        bottom = np.zeros(len(LANGUAGES))
        for column, label, color in fragments:
            values = subset[column].to_numpy() * 100
            axis.barh(
                LANGUAGES,
                values,
                left=bottom,
                label=label,
                color=color,
            )
            bottom += values
        axis.set_title(LABELS[tokenizer], fontweight="bold")
        axis.set_xlim(0, 100)
        axis.set_xlabel("Share of whitespace-delimited words (%)")

    axes[0].invert_yaxis()
    axes[1].legend(
        handles=axes[1].containers,
        labels=[item[1] for item in fragments],
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )
    figure.suptitle(
        "Word fragmentation across FLORES+ languages",
        x=0.08,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    figure.tight_layout()
    return save_figure(figure, "figure_3_word_fragmentation")


def diacritics_figure() -> list[str]:
    data = pd.read_csv(DIACRITICS_PATH)
    order = [
        ("ibo", "natlas_llama", "Igbo\nN-ATLaS / Llama 3"),
        ("ibo", "gemma4", "Igbo\nGemma 4"),
        ("yor", "natlas_llama", "Yoruba\nN-ATLaS / Llama 3"),
        ("yor", "gemma4", "Yoruba\nGemma 4"),
    ]
    values = []
    lower_errors = []
    upper_errors = []
    colors = []
    labels = []
    for language, tokenizer, label in order:
        row = data[
            (data["language_code"] == language)
            & (data["tokenizer"] == tokenizer)
        ].iloc[0]
        value = row["relative_token_reduction"] * 100
        values.append(value)
        lower_errors.append(value - row["reduction_ci95_low"] * 100)
        upper_errors.append(row["reduction_ci95_high"] * 100 - value)
        colors.append(COLORS["natlas"] if tokenizer == "natlas_llama" else COLORS["gemma4"])
        labels.append(label)

    figure, axis = plt.subplots(figsize=(8.2, 4.8))
    positions = np.arange(len(values))
    bars = axis.bar(
        positions,
        values,
        color=colors,
        width=0.62,
        yerr=np.vstack([lower_errors, upper_errors]),
        capsize=4,
        error_kw={"elinewidth": 1, "capthick": 1},
    )
    axis.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=9)
    axis.set_xticks(positions, labels)
    axis.set_ylabel("Reduction in total tokens after stripping marks (%)")
    axis.set_title(
        "Effect of removing diacritics from Igbo and Yoruba",
        loc="left",
        fontweight="bold",
    )
    axis.set_ylim(0, max(values) * 1.22)
    figure.tight_layout()
    return save_figure(figure, "figure_4_diacritics_effect")


def main() -> None:
    setup_style()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(SUMMARY_PATH)
    # N-ATLaS and Llama are identical on the corpus, so plot one combined series.
    plotted = summary[summary["tokenizer"].isin(["natlas", "gemma4"])]

    files = []
    files.extend(
        grouped_bars(
            plotted,
            "corpus_tokens_per_word",
            "fertility_ci95_low",
            "fertility_ci95_high",
            "Tokens per whitespace-delimited word",
            "Tokenization fertility by language",
            "figure_1_fertility",
        )
    )
    files.extend(
        grouped_bars(
            plotted,
            "relative_tax_vs_english",
            "tax_ci95_low",
            "tax_ci95_high",
            "Relative tokens per word (English = 1)",
            "Tokenizer tax relative to English",
            "figure_2_relative_tax",
            reference_line=1.0,
        )
    )
    files.extend(fragmentation_figure(plotted))
    if DIACRITICS_PATH.exists():
        files.extend(diacritics_figure())

    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SUMMARY_PATH),
        "figures": files,
        "note": (
            "N-ATLaS and Llama 3 are shown as one series because all corpus "
            "token-ID sequences and resulting metrics were identical."
        ),
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Created figures:")
    for path in files:
        print(f"  {path}")


if __name__ == "__main__":
    main()
