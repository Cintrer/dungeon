import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app import main
from app.database import get_session
from app.domain.hero_classes import Guerrier, Mage, Voleur, instancier_heros
from app.models.hero import Hero


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    main.app.dependency_overrides[get_session] = get_test_session
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()
    engine.dispose()


def create_account(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/register",
        json={"username": username, "password": "correct-horse-123"},
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        data={"username": username, "password": "correct-horse-123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_hero(client: TestClient, token: str) -> int:
    response = client.post(
        "/heroes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nom": "Test Hero",
            "classe": "mage",
            "force": 4,
            "agilite": 4,
            "intelligence": 2,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_hero_classes_calculate_damage(monkeypatch):
    warrior = Guerrier(force=3, agilite=2, intelligence=5)
    mage = Mage(force=3, agilite=2, intelligence=5)
    thief = Voleur(force=3, agilite=5, intelligence=2)

    assert warrior.calculer_degats() == (8, False)
    assert warrior.subir_degats(1) == 1
    assert warrior.subir_degats(4) == 3
    assert mage.calculer_degats() == (16, False)
    monkeypatch.setattr("app.domain.hero_classes.random.choice", lambda _: True)
    assert thief.calculer_degats() == (24, True)


def test_instancier_heros_rejects_unknown_class():
    hero = Hero(
        nom="Test",
        classe="inconnue",
        force=4,
        agilite=3,
        intelligence=3,
        pv=28,
        pv_max=28,
        salle_actuelle="entree",
    )

    with pytest.raises(ValueError, match="Classe inconnue"):
        instancier_heros(hero)


def test_hero_routes_require_auth_and_enforce_ownership(client: TestClient):
    first_token = create_account(client, "alice")
    hero_id = create_hero(client, first_token)
    second_token = create_account(client, "bob")

    assert client.get("/heroes").status_code == 401
    assert client.get(
        "/heroes", headers={"Authorization": f"Bearer {second_token}"}
    ).json() == []
    assert client.get(
        f"/heroes/{hero_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    ).status_code == 403


def test_combat_blocks_movement_and_awards_gold_on_victory(client: TestClient):
    token = create_account(client, "fighter")
    hero_id = create_hero(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post(
        f"/heroes/{hero_id}/move",
        headers=headers,
        json={"direction": "nord"},
    ).status_code == 200
    room_response = client.post(
        f"/heroes/{hero_id}/move",
        headers=headers,
        json={"direction": "ouest"},
    )
    assert room_response.status_code == 200
    assert room_response.json()["monstre"] == "Gobelin"

    blocked_move = client.post(
        f"/heroes/{hero_id}/move",
        headers=headers,
        json={"direction": "est"},
    )
    assert blocked_move.status_code == 409
    assert blocked_move.json()["detail"]["error"] == "IN_COMBAT"

    first_attack = client.post(f"/heroes/{hero_id}/attack", headers=headers)
    assert first_attack.status_code == 200
    assert first_attack.json()["issue"] == "en_cours"
    assert first_attack.json()["degats_infliges"] == 7
    assert first_attack.json()["degats_subis"] == 3

    second_attack = client.post(f"/heroes/{hero_id}/attack", headers=headers)
    assert second_attack.status_code == 200
    assert second_attack.json()["issue"] == "monstre_vaincu"
    assert second_attack.json()["or_gagne"] == 10
    assert second_attack.json()["pv_monstre"] == 0


def test_rest_is_blocked_during_combat_and_restores_health_afterward(
    client: TestClient,
):
    token = create_account(client, "resting")
    hero_id = create_hero(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        f"/heroes/{hero_id}/move",
        headers=headers,
        json={"direction": "nord"},
    )
    client.post(
        f"/heroes/{hero_id}/move",
        headers=headers,
        json={"direction": "ouest"},
    )

    blocked_rest = client.post(f"/heroes/{hero_id}/rest", headers=headers)
    assert blocked_rest.status_code == 409
    assert blocked_rest.json()["detail"]["error"] == "IN_COMBAT"

    client.post(f"/heroes/{hero_id}/attack", headers=headers)
    client.post(f"/heroes/{hero_id}/attack", headers=headers)
    rested = client.post(f"/heroes/{hero_id}/rest", headers=headers)

    assert rested.status_code == 200
    assert rested.json()["pv"] == rested.json()["pv_max"]
