from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

# Root directory containing all simulation folders
BASE_DIR = Path(__file__).parent / "SIM_files"


# ============================================================
# Plot definitions
# ============================================================

# "left_columns"  -> curves using the LEFT y-axis
# "right_columns" -> curves using the RIGHT y-axis
#
# Multiple columns can be plotted on either axis.
#
# Example:
#
# {
#     "left_columns": ["yaw", "pitch", "roll"],
#     "right_columns": ["speed"],
#     "filename": "attitude_speed.png",
#     "title": "UAV Attitude and Speed",
#     "left_ylabel": "Attitude [deg]",
#     "right_ylabel": "Speed [m/s]",
# }
#
# If you only need one y-axis, use:
#
# "right_columns": []


PLOTS = [

    # --------------------------------------------------------
    # C/N and Data Rate
    # --------------------------------------------------------

    {
        "left_columns": ["CN_total_downlink"],
        "right_columns": ["datarate_downlink"],

        "filename": "CN_datarate.png",
        "title": "Downlink C/N and Data Rate",

        "left_ylabel": "C/N [dB]",
        "right_ylabel": "Data Rate [Mbps]",
    },


    # --------------------------------------------------------
    # UAV attitude
    # --------------------------------------------------------

    {
        "left_columns": ["yaw", "pitch", "roll"],
        "right_columns": ["heading"],

        "filename": "attitude.png",
        "title": "UAV Attitude",

        "left_ylabel": "Attitude [deg]",
        "right_ylabel": "Heading [deg]",
    },


    # --------------------------------------------------------
    # UAV-to-Satellite distance
    # --------------------------------------------------------

    {
        "left_columns": ["uav_dist"],
        "right_columns": [],

        "filename": "dist_uav_sat.png",
        "title": "UAV-to-Satellite Distance",

        "left_ylabel": "Distance [m]",
        "satellite_switches": True,
    },


    # --------------------------------------------------------
    # Example: UAV attitude + speed
    # --------------------------------------------------------

    # {
    #     "left_columns": ["yaw", "pitch", "roll"],
    #     "right_columns": ["speed"],
    #
    #     "filename": "attitude_speed.png",
    #     "title": "UAV Attitude and Speed",
    #
    #     "left_ylabel": "Attitude [deg]",
    #     "right_ylabel": "Speed [m/s]",
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


    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    # Read exactly the first 500 lines of the CSV:
    #   line 1    = header
    #   lines 2-500 = first 499 data rows
    df = pd.read_csv(
        csv_file,
        sep=";",
        nrows=100
    )


    # --------------------------------------------------------
    # Check t_rel
    # --------------------------------------------------------

    if "t_rel" not in df.columns:

        print("  ERROR: Column 't_rel' not found.")

        continue


    # --------------------------------------------------------
    # Make sure t_rel is numeric
    # --------------------------------------------------------

    df["t_rel"] = pd.to_numeric(
        df["t_rel"],
        errors="coerce"
    )


    # ========================================================
    # Generate requested plots
    # ========================================================

    for plot_config in PLOTS:

        left_columns = plot_config.get(
            "left_columns",
            []
        )

        right_columns = plot_config.get(
            "right_columns",
            []
        )

        all_columns = (
            left_columns
            + right_columns
        )


        # ----------------------------------------------------
        # Check that requested columns exist
        # ----------------------------------------------------

        missing_columns = [
            column
            for column in all_columns
            if column not in df.columns
        ]

        if missing_columns:

            print(
                f"  WARNING: Missing columns "
                f"{missing_columns}"
            )

            print(
                "           Skipping this plot."
            )

            continue


        # ----------------------------------------------------
        # Convert requested columns to numeric
        # ----------------------------------------------------

        for column in all_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


        # ----------------------------------------------------
        # Print information about available data
        # ----------------------------------------------------

        print(
            f"\n  Plot: "
            f"{plot_config['filename']}"
        )

        for column in all_columns:

            valid_count = (
                df[column]
                .notna()
                .sum()
            )

            print(
                f"    {column}: "
                f"{valid_count} valid values"
            )


        # ====================================================
        # Create figure
        # ====================================================

        fig, ax_left = plt.subplots(
            figsize=(10, 6)
        )


        # ----------------------------------------------------
        # Create right axis if needed
        # ----------------------------------------------------

        if right_columns:

            ax_right = ax_left.twinx()

        else:

            ax_right = None


        # ====================================================
        # Shared color cycle
        # ====================================================

        # This is important because ax_left and ax_right
        # normally have separate color cycles.
        #
        # Using one shared color index guarantees that every
        # curve in the figure gets a different color.

        colors = (
            plt.rcParams["axes.prop_cycle"]
            .by_key()["color"]
        )

        color_index = 0


        # ====================================================
        # Plot left-axis curves
        # ====================================================

        for column in left_columns:

            valid = (
                df["t_rel"].notna()
                & df[column].notna()
            )

            ax_left.plot(
                df.loc[valid, "t_rel"],
                df.loc[valid, column],
                label=column,
                color=colors[
                    color_index % len(colors)
                ]
            )

            color_index += 1


        # ====================================================
        # Plot right-axis curves
        # ====================================================

        if ax_right is not None:

            for column in right_columns:

                valid = (
                    df["t_rel"].notna()
                    & df[column].notna()
                )

                ax_right.plot(
                    df.loc[valid, "t_rel"],
                    df.loc[valid, column],
                    label=column,
                    color=colors[
                        color_index % len(colors)
                    ]
                )

                color_index += 1


        # ====================================================
        # Satellite selection changes
        # ====================================================

        if plot_config.get(
            "satellite_switches",
            False
        ):

            if "sat_sel" in df.columns:

                # Find points where the selected satellite changes
                satellite_changes = (
                    df["sat_sel"].ne(
                        df["sat_sel"].shift()
                    )
                )

                # Get the corresponding time values
                switch_times = df.loc[
                    satellite_changes,
                    "t_rel"
                ]

                # Remove the first entry:
                # this is the initial satellite selection,
                # not a satellite switch
                switch_times = switch_times.iloc[1:]

                # Draw a vertical line at every satellite switch
                for switch_time in switch_times:

                    ax_left.axvline(
                        x=switch_time,
                        linestyle="--",
                        linewidth=1,
                        alpha=0.7
                    )

            else:

                print(
                    "  WARNING: Column 'sat_sel' not found "
                    "-> no satellite switch lines"
                )


        # ====================================================
        # Axis labels
        # ====================================================

        ax_left.set_xlabel(
            "t_rel [s]"
        )

        ax_left.set_ylabel(
            plot_config.get(
                "left_ylabel",
                "Value"
            )
        )

        if ax_right is not None:

            ax_right.set_ylabel(
                plot_config.get(
                    "right_ylabel",
                    "Value"
                )
            )


        # ====================================================
        # Title
        # ====================================================

        ax_left.set_title(
            plot_config.get(
                "title",
                ""
            )
        )


        # ====================================================
        # Grid
        # ====================================================

        ax_left.grid(
            True,
            alpha=0.3
        )


        # ====================================================
        # Combined legend
        # ====================================================

        lines_left, labels_left = (
            ax_left.get_legend_handles_labels()
        )

        if ax_right is not None:

            lines_right, labels_right = (
                ax_right.get_legend_handles_labels()
            )

        else:

            lines_right = []
            labels_right = []


        ax_left.legend(
            lines_left + lines_right,
            labels_left + labels_right
        )


        # ====================================================
        # Layout
        # ====================================================

        fig.tight_layout()


        # ====================================================
        # Save plot next to CSV
        # ====================================================

        output_file = (
            csv_file.parent
            / plot_config["filename"]
        )

        fig.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )


        # ====================================================
        # Close figure
        # ====================================================

        plt.close(fig)


        print(
            f"    Saved: {output_file}"
        )


# ============================================================
# Finished
# ============================================================

print("\nDone.")