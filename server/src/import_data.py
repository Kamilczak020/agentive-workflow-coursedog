import pandas as pd
from config import config
from neo4j import GraphDatabase

driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])

def create_node(tx, label, properties):
    query = f'CREATE (n:{label} {{'
    query += ', '.join([f'{key}: ${key}' for key in properties.keys()])
    query += '})'
    tx.run(query, **properties)

def create_relationship(tx, label1, label2, rel_type, properties1, properties2):
    query = f'''
    MATCH (a:{label1}), (b:{label2})
    WHERE {' AND '.join([f'a.{key} = ${key}' for key in properties1.keys()])}
      AND {' AND '.join([f'b.{key} = ${key}' for key in properties2.keys()])}
    CREATE (a)-[r:{rel_type}]->(b)
    '''
    tx.run(query, **properties1, **properties2)

student_info_df = pd.read_csv('documents/studentInfo.csv')
student_registration_df = pd.read_csv('documents/studentRegistration.csv')
student_assessment_df = pd.read_csv('documents/studentAssessment.csv')
student_vle_df = pd.read_csv('documents/studentVle.csv')
courses_df = pd.read_csv('documents/courses.csv')
assessments_df = pd.read_csv('documents/assessments.csv')
vle_df = pd.read_csv('documents/vle.csv')

def import_nodes(df, label):
    with driver.session() as session:
        for _, row in df.iterrows():
            properties = row.to_dict()
            session.write_transaction(create_node, label, properties)

def import_all_nodes():
    import_nodes(courses_df, 'Courses')
    import_nodes(assessments_df, 'Assessments')
    import_nodes(vle_df, 'Vle')
    import_nodes(student_info_df, 'StudentInfo')
    import_nodes(student_registration_df, 'StudentRegistration')
    import_nodes(student_assessment_df, 'StudentAssessment')
    import_nodes(student_vle_df, 'StudentVle')

def import_all_relationships():
    with driver.session() as session:
        for _, row in student_registration_df.iterrows():
            student_info_props = {
                'id_student': row['id_student'],
                'code_module': row['code_module'],
                'code_presentation': row['code_presentation']
            }
            student_registration_props = {
                'id_student': row['id_student'],
                'code_module': row['code_module'],
                'code_presentation': row['code_presentation']
            }
            session.write_transaction(
                create_relationship,
                'StudentInfo',
                'StudentRegistration',
                'HAS_REGISTRATION',
                student_info_props,
                student_registration_props
            )
        
        # Repeat for other relationships as needed...

driver.close()
