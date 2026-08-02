"""
Neo4j wrapper - OPTIONAL. If NEO4J_URI is not set, every function becomes a
graceful no-op so the rest of the app runs perfectly fine without it.
This lets you demo/deploy without Neo4j configured, and turn it on later
(Phase 3) just by filling in the .env values - no code changes needed.
"""
from config import settings

_enabled = bool(settings.NEO4J_URI)
_driver = None

if _enabled:
    from neo4j import GraphDatabase
    _driver = GraphDatabase.driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )


def is_enabled() -> bool:
    return _enabled


def add_employee_skill(employee_name: str, department: str, skill: str):
    if not _enabled:
        return
    with _driver.session() as session:
        session.run(
            """
            MERGE (e:Employee {name: $employee_name})
            MERGE (d:Department {name: $department})
            MERGE (s:Skill {name: $skill})
            MERGE (e)-[:BELONGS_TO]->(d)
            MERGE (e)-[:HAS_SKILL]->(s)
            """,
            employee_name=employee_name, department=department, skill=skill,
        )


def add_solution(employee_name: str, problem: str, solution_summary: str, sop_title: str = None):
    if not _enabled:
        return
    with _driver.session() as session:
        session.run(
            """
            MERGE (e:Employee {name: $employee_name})
            MERGE (p:Problem {name: $problem})
            MERGE (e)-[:SOLVED]->(p)
            """,
            employee_name=employee_name, problem=problem,
        )
        if sop_title:
            session.run(
                """
                MERGE (p:Problem {name: $problem})
                MERGE (sop:SOP {title: $sop_title})
                MERGE (p)-[:DOCUMENTED]->(sop)
                """,
                problem=problem, sop_title=sop_title,
            )


def find_experts_by_skill(skill: str):
    if not _enabled:
        return []
    with _driver.session() as session:
        result = session.run(
            """
            MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill)
            WHERE toLower(s.name) CONTAINS toLower($skill)
            RETURN DISTINCT e.name AS name
            LIMIT 20
            """,
            skill=skill,
        )
        return [record["name"] for record in result]


def graph_stats():
    if not _enabled:
        return {"enabled": False, "nodes": 0, "relationships": 0}
    with _driver.session() as session:
        nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        return {"enabled": True, "nodes": nodes, "relationships": rels}
