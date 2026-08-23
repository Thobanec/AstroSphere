def print_solar_system_overview(now, results):
    print()
    print("=" * 75)
    print("                     SOLAR SYSTEM OVERVIEW")
    print("=" * 75)

    print()
    print(
        f"Calculation time: "
        f"{now.utc_strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    print()
    print(
        f"{'OBJECT':<15}"
        f"{'FROM SUN (KM)':>22}"
        f"{'FROM EARTH (KM)':>25}"
    )

    print("-" * 75)

    for result in results:
        print(
            f"{result['name']:<15}"
            f"{result['distance_from_sun']:>22,.0f}"
            f"{result['distance_from_earth']:>25,.0f}"
        )

    print("-" * 75)

    print()
    print(f"Tracked Solar System objects: {len(results)}")
    print()