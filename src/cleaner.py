from pathlib import Path
import pandas as pd

RAW_INPUT = Path("data/raw/raw_weather.csv")
CLEAN_OUTPUT = Path("data/processed/cleaned_weather.csv")


def summarize_dataframe(label: str, df: pd.DataFrame) -> None:
    print(f"\n--- {label} ---")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("Missing values per column:")
    print(df.isna().sum().to_dict())
    print(f"Exact duplicate rows: {df.duplicated().sum()}")


def clean_and_transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    str_cols = [
        "city",
        "country",
        "condition_raw",
        "temp_raw",
        "wind_raw",
        "local_time_raw",
        "source_url",
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    df = df.dropna(subset=["city", "country", "temp_raw"])
    df = df.drop_duplicates(subset=["city", "country"], keep="first")
    df["condition_clean"] = df["condition_raw"].fillna("Not Listed")

    df["temp_f"] = pd.to_numeric(
        df["temp_raw"].str.extract(r"(-?\d+(?:\.\d+)?)", expand=False),
        errors="coerce",
    )
    df["wind_mph"] = pd.to_numeric(
        df["wind_raw"].str.extract(r"(-?\d+(?:\.\d+)?)", expand=False),
        errors="coerce",
    )

    df = df.dropna(subset=["temp_f"]).copy()
    df["temp_c"] = ((df["temp_f"] - 32.0) * 5.0 / 9.0).round(1)
    df["temp_tier"] = pd.cut(
        df["temp_f"],
        bins=[-150, 50, 74.9, 200],
        labels=["Cold / Chilly (<50°F)", "Mild (50–74°F)", "Warm / Hot (75°F+)"],
    )

    ordered_cols = [
        "city",
        "country",
        "temp_f",
        "temp_c",
        "temp_tier",
        "wind_mph",
        "condition_clean",
        "local_time_raw",
        "source_url",
    ]
    return df[ordered_cols].reset_index(drop=True)


def print_insights(clean_df: pd.DataFrame) -> None:
    print("\n--- Grouped Summary by Temperature Tier ---")
    summary = clean_df.groupby("temp_tier", observed=False).agg(
        city_count=("city", "count"),
        avg_temp_f=("temp_f", "mean"),
        avg_temp_c=("temp_c", "mean"),
        avg_wind_mph=("wind_mph", "mean"),
    )
    print(summary.round(1))

    print("\n--- Sample Cleaned Rows ---")
    print(clean_df.head(5).to_string(index=False))


def save_cleaned_csv(clean_df: pd.DataFrame, output_path: Path = CLEAN_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    raw_df = pd.read_csv(RAW_INPUT)
    summarize_dataframe("BEFORE CLEANING (Raw)", raw_df)

    clean_df = clean_and_transform(raw_df)
    summarize_dataframe("AFTER CLEANING (Processed)", clean_df)
    print_insights(clean_df)

    out_path = save_cleaned_csv(clean_df, CLEAN_OUTPUT)
    print(f"\nSaved cleaned dataset -> {out_path}")


if __name__ == "__main__":
    main()