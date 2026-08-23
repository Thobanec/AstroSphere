def print_orbital_report(
    results,
    object_name,
    reference_body="Earth",
    interval_days=1,
):
    if not results:
        print("No orbital data available.")
        return

    closest = min(
        results,
        key=lambda result: result["distance_km"],
    )

    farthest = max(
        results,
        key=lambda result: result["distance_km"],
    )

    start_date = results[0]["date"]
    end_date = results[-1]["date"]

    initial_km = results[0]["distance_km"]
    final_km = results[-1]["distance_km"]

    minimum_km = closest["distance_km"]
    maximum_km = farthest["distance_km"]
    variation_km = maximum_km - minimum_km

    average_km = sum(
        result["distance_km"]
        for result in results
    ) / len(results)

    distance_change_km = final_km - initial_km

    if initial_km != 0:
        percentage_change = (
            distance_change_km / initial_km
        ) * 100
    else:
        percentage_change = 0.0

    if distance_change_km < 0:
        trend = "Getting closer"
    elif distance_change_km > 0:
        trend = "Getting farther apart"
    else:
        trend = "No overall change"

    print()
    print("=" * 70)
    print("ASTROSPHERE")
    print(
        f"{reference_body} -> {object_name} Orbital Analysis"
    )
    print("=" * 70)

    print()
    print("ANALYSIS PERIOD")
    print("-" * 70)

    print(
        f"Start date:        "
        f"{start_date.strftime('%d %B %Y')}"
    )

    print(
        f"End date:          "
        f"{end_date.strftime('%d %B %Y')}"
    )

    print(
        f"Samples:           "
        f"{len(results)}"
    )

    print(
        f"Sampling interval: "
        f"{interval_days} day(s)"
    )

    print()
    print("CLOSEST APPROACH")
    print("-" * 70)

    print(
        f"Date:              "
        f"{closest['date'].strftime('%d %B %Y')}"
    )

    print(
        f"Distance:          "
        f"{minimum_km:,.0f} km"
    )

    print(
        f"Distance:          "
        f"{minimum_km / 1_000_000:.3f} million km"
    )

    print()
    print("FARTHEST APPROACH")
    print("-" * 70)

    print(
        f"Date:              "
        f"{farthest['date'].strftime('%d %B %Y')}"
    )

    print(
        f"Distance:          "
        f"{maximum_km:,.0f} km"
    )

    print(
        f"Distance:          "
        f"{maximum_km / 1_000_000:.3f} million km"
    )

    print()
    print("DISTANCE RANGE")
    print("-" * 70)

    print(
        f"Minimum:           "
        f"{minimum_km / 1_000_000:.3f} million km"
    )

    print(
        f"Maximum:           "
        f"{maximum_km / 1_000_000:.3f} million km"
    )

    print(
        f"Variation:         "
        f"{variation_km / 1_000_000:.3f} million km"
    )

    print()
    print("DISTANCE STATISTICS")
    print("-" * 70)

    print(
        f"Initial distance:  "
        f"{initial_km / 1_000_000:.3f} million km"
    )

    print(
        f"Final distance:    "
        f"{final_km / 1_000_000:.3f} million km"
    )

    print(
        f"Average distance:  "
        f"{average_km / 1_000_000:.3f} million km"
    )

    print(
        f"Distance change:   "
        f"{distance_change_km / 1_000_000:+.3f} million km"
    )

    print(
        f"Percentage change: "
        f"{percentage_change:+.3f}%"
    )

    print(
        f"Trend:             "
        f"{trend}"
    )

    print()
    print("=" * 70)