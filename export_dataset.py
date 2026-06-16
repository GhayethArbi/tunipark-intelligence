import csv
import math
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "parking_db",
    "user": "postgres",
    "password": "system",
}


DESTINATIONS = [
    ("Tunis", 36.8065, 10.1815),
    ("Ariana", 36.8625, 10.1956),
    ("Ben Arous", 36.7531, 10.2189),
    ("Manouba", 36.8101, 10.0956),
    ("Lac 1", 36.8384, 10.2392),
    ("Lac 2", 36.8465, 10.2721),
    ("Aouina", 36.8593, 10.2705),
    ("La Marsa", 36.8782, 10.3247),
    ("Sidi Bou Said", 36.8691, 10.3417),
    ("Carthage", 36.8529, 10.3230),
]


def haversine_km(lat1, lng1, lat2, lng2):
    radius = 6371

    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )

    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_score(distance_km, availability_score, conversion_rate, extension_rate, price):
    distance_score = (1 - min(distance_km / 8, 1)) * 35
    availability_score_part = availability_score * 25
    conversion_score = conversion_rate * 25
    extension_score = extension_rate * 10
    price_score = (1 - min(price / 30, 1)) * 5

    score = (
        distance_score
        + availability_score_part
        + conversion_score
        + extension_score
        + price_score
    )

    return max(0, min(100, round(score, 2)))


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.title,
            p.location,
            p."availablePlaces",
            p."maxPlaces",
            t."pricePerDay"
        FROM "Parking" p
        LEFT JOIN "Tariff" t ON t."parkingId" = p.id
        WHERE p.status = 'ACTIVE'
          AND p."archivedAt" IS NULL
    """)

    parkings = cur.fetchall()

    rows = []

    for parking in parkings:
        parking_id, title, location, available_places, max_places, price = parking

        if not location:
            continue

        lat = float(location.get("lat"))
        lng = float(location.get("lng"))

        price = float(price or 0)
        availability_score = available_places / max_places if max_places > 0 else 0

        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE "interactionType" = 'VIEW') AS views,
                COUNT(*) FILTER (WHERE "interactionType" = 'START_SESSION') AS starts,
                COUNT(*) FILTER (WHERE "interactionType" = 'EXTEND_SESSION') AS extensions
            FROM "ParkingInteraction"
            WHERE "parkingId" = %s
        """, (parking_id,))

        views, starts, extensions = cur.fetchone()

        views = views or 0
        starts = starts or 0
        extensions = extensions or 0

        conversion_rate = starts / views if views > 0 else 0
        extension_rate = extensions / starts if starts > 0 else 0

        for destination_name, dest_lat, dest_lng in DESTINATIONS:
            distance_km = haversine_km(dest_lat, dest_lng, lat, lng)

            score = calculate_score(
                distance_km=distance_km,
                availability_score=availability_score,
                conversion_rate=conversion_rate,
                extension_rate=extension_rate,
                price=price,
            )

            rows.append({
                "parkingId": parking_id,
                "parkingTitle": title,
                "destination": destination_name,
                "distanceKm": round(distance_km, 2),
                "availabilityScore": round(availability_score, 2),
                "conversionRate": round(conversion_rate, 2),
                "extensionRate": round(extension_rate, 2),
                "price": round(price, 2),
                "views": views,
                "starts": starts,
                "extensions": extensions,
                "score": score,
            })

    with open("dataset.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "parkingId",
                "parkingTitle",
                "destination",
                "distanceKm",
                "availabilityScore",
                "conversionRate",
                "extensionRate",
                "price",
                "views",
                "starts",
                "extensions",
                "score",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    cur.close()
    conn.close()

    print(f"dataset.csv generated successfully with {len(rows)} rows.")


if __name__ == "__main__":
    main()