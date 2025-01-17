def get_data_model_prompt():
    return '''
        The available knowledge is entirely contained in a neo4j graph database
        Below you will find the entire data schema available to access.
        
        ### Course
        - course_id - the id of the course
        - department_ids - the ids of the departments the course belongs to
        - description - the description of the course
        - section_types - the types of sections this course is available in
        - name - the name of the course
        - year - the year in which the course is ran

        ### Section
        - section_id - the id of the section
        - course_id - the id of the course this section is for
        - professor_ids - the ids of the professors, for whom the section operates
        - available_seats - the number of available seats left in this section
        - enrollment - the number of taken seats in this section. enrollment + available_seats = total_seats
        - year - the year in which the section is ran

        ### Professor
        - professor_id - the id of the professor
        - email - professor\'s email
        - name - professor\'s name
        - type - professor\'s type

        ### Department
        - department_id - the id of the department
        - department_name - the name of the department

        Besides the node schema, nodes are connected with the following relationships:
        - (c:Course)-[:BELONGS_TO]->(d:Department) (one-to-many)
        - (s:Section)-[:FOR]->(c:Course) (one-to-one)
        - (p:Professor)-[:TEACHES]->(s:Section) (one-to-many)

        There is also semantic search indexes available:
        - course_description - semantic search over embbeded course descriptions
    '''

