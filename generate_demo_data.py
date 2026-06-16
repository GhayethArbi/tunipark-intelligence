import psycopg2
import random
import uuid
import json
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="parking_db",
    user="postgres",
    password="system",
)

cur = conn.cursor()

REGIONS = [
    ("Tunis", 10, 36.8065, 10.1815),
    ("Ariana", 9, 36.8625, 10.1956),
    ("Ben Arous", 5, 36.7531, 10.2189),
    ("Manouba", 9, 36.8101, 10.0956),
    ("Lac 1", 10, 36.8384, 10.2392),
    ("Lac 2", 10, 36.8465, 10.2721),
    ("Aouina", 6, 36.8593, 10.2705),
    ("La Marsa", 12, 36.8782, 10.3247),
    ("Sidi Bou Said", 10, 36.8691, 10.3417),
    ("Carthage", 10, 36.8529, 10.3230),
]

def random_offset():
    return random.uniform(-0.01, 0.01)

owners = []
drivers = []

# print("Creating owners...")

# for i in range(1, 11):
#     user_id = str(uuid.uuid4())

#     cur.execute("""
#         INSERT INTO "User" (
#             id,
#             "firstName",
#             "lastName",
#             email,
#             "phoneNumber",
#             password,
#             role,
#             "isEmailVerified",
#             "isPhoneNumberVerified",
#             "createdAt",
#             "updatedAt",
#             "resetTokenVersion"
#         )
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),0)
#     """, (
#         user_id,
#         f"Owner{i}",
#         "TuniPark",
#         f"owner{i}@tunipark.tn",
#         f"2{i:07d}",
#         "demo_password",
#         "PARKING_OWNER",
#         True,
#         True,
#     ))

#     owners.append(user_id)

# print("Creating drivers...")

# for i in range(1, 101):
#     user_id = str(uuid.uuid4())

#     cur.execute("""
#         INSERT INTO "User" (
#             id,
#             "firstName",
#             "lastName",
#             email,
#             "phoneNumber",
#             password,
#             role,
#             "isEmailVerified",
#             "isPhoneNumberVerified",
#             "createdAt",
#             "updatedAt",
#             "resetTokenVersion"
#         )
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),0)
#     """, (
#         user_id,
#         f"Driver{i}",
#         "TuniPark",
#         f"driver{i}@tunipark.tn",
#         f"3{i:07d}",
#         "demo_password",
#         "USER",
#         True,
#         True,
#     ))

#     drivers.append(user_id)

# print("Owners:", len(owners))
# print("Drivers:", len(drivers))
print("Loading existing owners...")

cur.execute("""
    SELECT id
    FROM "User"
    WHERE role = 'PARKING_OWNER'
""")

owners = [row[0] for row in cur.fetchall()]

print("Owners:", len(owners))


print("Loading existing drivers...")

cur.execute("""
    SELECT id
    FROM "User"
    WHERE role = 'USER'
""")

drivers = [row[0] for row in cur.fetchall()]

print("Drivers:", len(drivers))

print("Creating parkings...")

parking_ids = []

owner_index = 0

for region_name, count, center_lat, center_lng in REGIONS:
    for i in range(1, count + 1):

        parking_id = str(uuid.uuid4())

        owner_id = owners[owner_index % len(owners)]
        owner_index += 1

        max_places = random.randint(10, 80)
        available_places = random.randint(1, max_places)

        latitude = center_lat + random_offset()
        longitude = center_lng + random_offset()

        cur.execute("""
            INSERT INTO "Parking" (
                id,
                title,
                type,
                "openingTime",
                "closingTime",
                "spotType",
                description,
                characteristics,
                pictures,
                location,
                status,
                "availablePlaces",
                "maxPlaces",
                "vehicleTypes",
                "accessMode",
                "ownerId",
                "createdAt",
                "updatedAt"
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s::"ParkingVehicleType"[],%s,%s,NOW(),NOW()
            )
        """, (
            parking_id,
            f"{region_name} Parking {i}",
            "PRIVATE" if random.random() < 0.8 else "PUBLIC",
            "07:00",
            "22:00",
            random.choice([
                "OUTDOOR",
                "COVERED",
                "GARAGE",
                "UNDERGROUND"
            ]),
            f"Smart parking located in {region_name}",
            random.sample(
                ["SECURE", "CAMERA", "LIGHTING"],
                random.randint(1, 3)
            ),
            [],
            json.dumps({
                "lat": latitude,
                "lng": longitude,
                "address": region_name,
            }),
            "ACTIVE",
            available_places,
            max_places,
            '{SMALL,MEDIUM}',
            random.choice([
                "FREQUENT",
                "OCCASIONAL"
            ]),
            owner_id,
        ))

        parking_ids.append(parking_id)

        tariff_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO "Tariff" (
                id,
                "pricePerUnit",
                "pricePerDay",
                "pricePerMonth",
                "minDuration",
                "maxDuration",
                "parkingId",
                "createdAt",
                "updatedAt"
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,NOW(),NOW()
            )
        """, (
            tariff_id,
            random.randint(2, 5),
            random.randint(5, 30),
            random.randint(80, 300),
            1,
            30,
            parking_id,
        ))

print("Parkings:", len(parking_ids))
print("Creating sessions, payments and interactions...")

brands = ["Toyota", "Volkswagen", "Peugeot", "Renault", "Hyundai", "Kia", "BMW", "Mercedes"]
models = ["Yaris", "Golf", "208", "Clio", "i20", "Rio", "Serie 1", "Classe A"]

total_sessions = 0
total_payments = 0
total_interactions = 0

start_history = datetime.now() - timedelta(days=90)

for parking_id in parking_ids:
    sessions_count = random.randint(30, 200)
    views_count = random.randint(100, 1500)
    starts_count = random.randint(20, 400)
    extensions_count = random.randint(0, min(150, starts_count))

    for _ in range(views_count):
        interaction_id = str(uuid.uuid4())
        driver_id = random.choice(drivers)
        created_at = start_history + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(6, 23),
            minutes=random.randint(0, 59),
        )

        cur.execute("""
            INSERT INTO "ParkingInteraction" (
                id,
                "userId",
                "parkingId",
                "interactionType",
                "createdAt"
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            interaction_id,
            driver_id,
            parking_id,
            "VIEW",
            created_at,
        ))

        total_interactions += 1

    for _ in range(starts_count):
        interaction_id = str(uuid.uuid4())
        driver_id = random.choice(drivers)
        created_at = start_history + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(6, 23),
            minutes=random.randint(0, 59),
        )

        cur.execute("""
            INSERT INTO "ParkingInteraction" (
                id,
                "userId",
                "parkingId",
                "interactionType",
                "createdAt"
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            interaction_id,
            driver_id,
            parking_id,
            "START_SESSION",
            created_at,
        ))

        total_interactions += 1

    for _ in range(extensions_count):
        interaction_id = str(uuid.uuid4())
        driver_id = random.choice(drivers)
        created_at = start_history + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(6, 23),
            minutes=random.randint(0, 59),
        )

        cur.execute("""
            INSERT INTO "ParkingInteraction" (
                id,
                "userId",
                "parkingId",
                "interactionType",
                "createdAt"
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            interaction_id,
            driver_id,
            parking_id,
            "EXTEND_SESSION",
            created_at,
        ))

        total_interactions += 1

    for _ in range(sessions_count):
        session_id = str(uuid.uuid4())
        payment_id = str(uuid.uuid4())
        driver_id = random.choice(drivers)

        duration_hours = random.randint(1, 8)

        start_time = start_history + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59),
        )

        end_time = start_time + timedelta(hours=duration_hours)

        status = "EXPIRED" if end_time < datetime.now() else "ACTIVE"
        paid = random.random() < 0.95

        cur.execute("""
            INSERT INTO "ParkingSession" (
                id,
                "parkingId",
                "vehiclePlate",
                "vehicleBrand",
                "vehicleModel",
                "userId",
                "startTime",
                "endTime",
                status,
                "paidDuration",
                "createdAt",
                "updatedAt"
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
        """, (
            session_id,
            parking_id,
            f"{random.randint(100,999)} TU {random.randint(1000,9999)}",
            random.choice(brands),
            random.choice(models),
            driver_id,
            start_time,
            end_time,
            status,
            duration_hours,
        ))

        total_sessions += 1

        cur.execute("""
            INSERT INTO "Payment" (
                id,
                "sessionId",
                provider,
                amount,
                status,
                "providerReference",
                "paidAt",
                "createdAt",
                "updatedAt"
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
        """, (
            payment_id,
            session_id,
            "FLOUCI",
            duration_hours * random.randint(2, 5),
            "PAID" if paid else "FAILED",
            f"FL-{payment_id[:8]}",
            end_time if paid else None,
        ))

        total_payments += 1

print("Sessions:", total_sessions)
print("Payments:", total_payments)
print("Interactions:", total_interactions)
conn.commit()

cur.close()
conn.close()

print("Changes committed.")