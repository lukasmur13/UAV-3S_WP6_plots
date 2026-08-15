from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

# Root directory containing all simulation folders
BASE_DIR = Path(__file__).parent / "SIM_files"


# Define the plots you want to generate.
#
# "columns" can contain one or multiple CSV headers.
#
# Example:
# {
#     "columns": ["column_A"],
#     "filename": "plot_column_A.png",
#     "title": "Column A over time",
#     "ylabel": "Column A"
# }
#
# Multiple columns in one plot:
#
# {
#     "columns": ["column_A", "column_B", "column_C"],
#     "filename": "comparison.png",
#     "title": "Comparison",
#     "ylabel": "Value"
# }

PLOTS = [
    {
        "columns": ["CN_total_downlink"],
        "filename": "C_over_N_downlink.png",
        "title": "C/N Downlink",
        "ylabel": "C/N [dB]",
    },
    {
        "columns": ["datarate_downlink"],
        "filename": "datarate_dowlink.png",
        "title": "Datarate Downlink",
        "ylabel": "Datarate [Mbit/s]",
    },
    # Example of multiple columns in one plot:
    #
    # {
    #     "columns": ["column_A", "column_B"],
    #     "filename": "plot_A_B.png",
    #     "title": "Column A and B",
    #     "ylabel": "Value",
    # },
]


# ============================================================
# Find CSV files
# ============================================================

csv_files = list(BASE_DIR.rglob("*.csv"))

print(f"Found {len(csv_files)} CSV files.")


# ============================================================
# Process each CSV
# ============================================================

for csv_file in csv_files:

    print(f"\nProcessing: {csv_file}")

    # Read CSV
    df = pd.read_csv(csv_file, sep=";")


    # --------------------------------------------------------
    # Check that t_rel exists
    # --------------------------------------------------------

    if "t_rel" not in df.columns:
        print("  ERROR: Column 't_rel' not found.")
        continue


    # --------------------------------------------------------
    # Generate all requested plots
    # --------------------------------------------------------

    for plot_config in PLOTS:

        columns = plot_config["columns"]

        # Check that all requested columns exist
        missing_columns = [
            column for column in columns
            if column not in df.columns
        ]

        if missing_columns:
            print(
                f"  WARNING: Missing columns "
                f"{missing_columns} -> skipping plot"
            )
            continue


        # Create figure
        plt.figure(figsize=(10, 6))


        # Plot every requested column
        for column in columns:

            plt.plot(
                df["t_rel"],
                df[column],
                label=column
            )


        # Formatting
        plt.xlabel("t_rel")
        plt.ylabel(plot_config.get("ylabel", "Value"))
        plt.title(plot_config.get("title", ""))

        # Only show legend if there is more than one column
        # (you can remove this condition if you always want one)
        if len(columns) > 1:
            plt.legend()

        plt.grid(True)
        plt.tight_layout()


        # Save next to the CSV
        output_file = csv_file.parent / plot_config["filename"]

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"  Saved: {output_file}")


print("\nDone.")