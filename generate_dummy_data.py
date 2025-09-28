"""
Generates dummy candidate JSON for local testing.

Run from terminal:
    python generate_dummy_data.py

Or call generate_dummy_candidate() from other modules.
"""

import random
from datetime import datetime, timezone

def generate_dummy_candidate():
    first_names = ["Aditi", "Karan", "Meera", "Rohan", "Priya", "Saubhagya"]
    last_names = ["Sharma", "Patel", "Mishra", "Kumar", "Singh", "Das"]
    tech_pools = [
        ["Python", "Django", "PostgreSQL"],
        ["React", "TypeScript", "Node.js"],
        ["Java", "Spring Boot", "MySQL"],
        ["Python", "Pandas", "scikit-learn"],
        ["AWS", "Terraform", "Docker"]
    ]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    candidate = {
        "full_name": name,
        "email": f"{name.replace(' ', '.').lower()}@example.com",
        "phone": f"+91{random.randint(9000000000, 9999999999)}",
        "years_experience": round(random.uniform(0.5, 8.0), 1),
        "desired_positions": ["Software Engineer"],
        "location": random.choice(["Bengaluru, India", "Mumbai, India", "Pune, India", "Delhi, India"]),
        "tech_stack": random.choice(tech_pools),
        # timezone-aware UTC datetime
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    return candidate

if __name__ == "__main__":
    import json, os
    candidate = generate_dummy_candidate()
    os.makedirs("data", exist_ok=True)
    with open("data/dummy_candidate.json", "w", encoding="utf-8") as f:
        json.dump(candidate, f, indent=2)
    print("Dummy candidate written to data/dummy_candidate.json")
