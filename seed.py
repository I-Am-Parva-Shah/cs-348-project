from app import app, db, Project, Developer

with app.app_context():
    # Creates the tables if they don't exist yet
    db.create_all()

    # Check if we already have data to avoid duplicates
    if not Project.query.first():
        # Create projects
        p1 = Project(name="Website Redesign")
        p2 = Project(name="Mobile App Launch")

        # Create developers
        d1 = Developer(name="Alice Smith")
        d2 = Developer(name="Bob Jones")

        # Add to database and save
        db.session.add_all([p1, p2, d1, d2])
        db.session.commit()
        print("Database seeded successfully.")
    else:
        print("Database already has data.")