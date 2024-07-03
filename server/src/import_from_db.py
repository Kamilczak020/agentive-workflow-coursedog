from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from neo4j import GraphDatabase
from config import config

try:
    client = MongoClient(config['mongo']['uri'])
    print('connected successfully')
except ConnectionFailure as error:
    print(error)

def import_all_from_db():
    db = client['abraham_baldwin']
    driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])

    # import_all_nodes(db, driver)
    import_all_relationships(db, driver)

    driver.close()

def import_all_nodes(db, driver):
    with driver.session() as session:
        import_courses_from_db(db, session)
        import_sections_from_db(db, session)
        import_professors_from_db(db, session)
        import_departments_from_db(db, session)

def import_all_relationships(db, driver):
    with driver.session() as session:
        course_to_department(db, session)
        section_to_course(db, session)
        section_to_department(db, session)
        section_to_professor(db, session)

def import_courses_from_db(db, session):
    collection = db['courses.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        properties = {
            'course_id': entity['_id'],
            'department_ids': entity['departments'],
            'description': entity['description'],
            'section_types': entity['sectionTypes'],
            'name': entity['name'],
            'year': 2024
        }

        session.run(f'''
            CREATE (n:Course)
            SET n = $properties
        ''', properties=properties)

def import_sections_from_db(db, session):
    collection = db['sections.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        properties = {
            'section_id': entity['_id'],
            'course_id': entity['courseId'],
            'professor_ids': entity['professors'],
            'available_seats': entity['availableSeats'],
            'enrollment': entity['enrollment'],
            'year': 2024
        }

        session.run(f'''
            CREATE (n:Section)
            SET n = $properties
        ''', properties=properties)

def import_professors_from_db(db, session):
    collection = db['professors']

    from_db = collection.find({ 'status': 'Active' })

    for entity in from_db:
        properties = {
            'professor_id': entity['_id'],
            'email': entity['email'],
            'name': f'''{entity['firstName']} {entity['lastName']}''',
            'type': entity['type']
        }

        session.run(f'''
            CREATE (n:Professor)
            SET n = $properties
        ''', properties=properties)

def import_departments_from_db(db, session):
    collection = db['departments']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        properties = {
            'department_id': entity['_id'],
            'display_name': entity['displayName'],
        }

        session.run(f'''
            CREATE (n:Department)
            SET n = $properties
        ''', properties=properties)

def course_to_department(db, session):
    collection = db['courses.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        session.run(f'''
            MATCH (c:Course {{ course_id: $course_id }})
            WHERE c.department_ids IS NOT NULL
            UNWIND c.department_ids AS dept_id
            MATCH (d:Department {{ department_id: dept_id }})
            MERGE (c)-[:BELONGS_TO]->(d)
        ''', course_id=entity['_id'])

def section_to_course(db, session):
    collection = db['sections.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        session.run(f'''
            MATCH (s:Section {{ section_id: $section_id }})
            WHERE s.course_id IS NOT NULL
            MATCH (c:Course {{ course_id: s.course_id }})
            MERGE (s)-[:FOR]->(c)
        ''', section_id=entity['_id'])

def section_to_department(db, session):
    collection = db['sections.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        session.run(f'''
            MATCH (s:Section {{ section_id: $section_id }})
            WHERE s.department_id IS NOT NULL
            MATCH (d:Department {{ department_id: s.department_id }})
            MERGE (s)-[:BELONGS_TO]->(d)
        ''', section_id=entity['_id'])

def section_to_professor(db, session):
    collection = db['sections.2024.8']

    from_db = collection.find({ 'status': 'Active' })
    for entity in from_db:
        session.run(f'''
            MATCH (s:Section {{ section_id: $section_id }})
            WHERE s.professor_ids IS NOT NULL
            UNWIND s.professor_ids AS prof_id
            MATCH (p:Professor {{ professor_id: prof_id }})
            MERGE (p)-[:TEACHES]->(s)
        ''', section_id=entity['_id'])
