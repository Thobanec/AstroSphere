import matplotlib.pyplot as plt


def plot_distance(
    results,
    object_name,
    reference_body="Earth",
):
    if not results:
        print("No data available for visualization.")
        return

    dates = [
        result["date"]
        for result in results
    ]

    distances_million_km = [
        result["distance_km"] / 1_000_000
        for result in results
    ]

    plt.figure(figsize=(12, 6))

    plt.plot(
        dates,
        distances_million_km,
        marker="o",
    )

    plt.title(
        f"{reference_body} → "
        f"{object_name} Distance Over Time"
    )

    plt.xlabel("Date")
    plt.ylabel("Distance (million km)")

    plt.grid(True)
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()