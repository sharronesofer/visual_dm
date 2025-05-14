import pytest
from flask import Flask
from app import create_app
from app.core.database import db
from flask_jwt_extended import create_access_token

def auth_header(user_id=1):
    token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_and_get_quest(client):
    resp = client.post('/api/v1/quests', json={
        'title': 'Test Quest',
        'description': 'A quest for testing.'
    }, headers=auth_header())
    assert resp.status_code == 201
    quest_id = resp.get_json()['id']
    get_resp = client.get(f'/api/v1/quests/{quest_id}', headers=auth_header())
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['title'] == 'Test Quest'

def test_update_quest(client):
    resp = client.post('/api/v1/quests', json={
        'title': 'Update Quest',
        'description': 'To be updated.'
    }, headers=auth_header())
    quest_id = resp.get_json()['id']
    update_resp = client.put(f'/api/v1/quests/{quest_id}', json={
        'description': 'Updated!'
    }, headers=auth_header())
    assert update_resp.status_code == 200
    assert update_resp.get_json()['description'] == 'Updated!'

def test_delete_quest(client):
    resp = client.post('/api/v1/quests', json={
        'title': 'Delete Quest',
        'description': 'To be deleted.'
    }, headers=auth_header())
    quest_id = resp.get_json()['id']
    del_resp = client.delete(f'/api/v1/quests/{quest_id}', headers=auth_header())
    assert del_resp.status_code == 200
    get_resp = client.get(f'/api/v1/quests/{quest_id}', headers=auth_header())
    assert get_resp.status_code == 404

def test_quest_progress_update(client):
    resp = client.post('/api/v1/quests', json={
        'title': 'Progress Quest',
        'description': 'Testing progress.'
    }, headers=auth_header())
    quest_id = resp.get_json()['id']
    put_resp = client.put(f'/api/v1/quests/{quest_id}/progress', json={
        'progress': {'stage': 'halfway'}
    }, headers=auth_header())
    assert put_resp.status_code == 200
    get_resp = client.get(f'/api/v1/quests/{quest_id}/progress', headers=auth_header())
    assert get_resp.status_code == 200
    assert get_resp.get_json()['progress']['stage'] == 'halfway'

def test_quest_complete_and_rewards(client):
    resp = client.post('/api/v1/quests', json={
        'title': 'Complete Quest',
        'description': 'Testing completion.',
        'rewards': [{'type': 'gold', 'amount': 100}]
    }, headers=auth_header())
    quest_id = resp.get_json()['id']
    complete_resp = client.post(f'/api/v1/quests/{quest_id}/complete', headers=auth_header())
    assert complete_resp.status_code == 200
    rewards_resp = client.get(f'/api/v1/quests/{quest_id}/rewards', headers=auth_header())
    assert rewards_resp.status_code == 200
    rewards = rewards_resp.get_json()['rewards']
    assert any(r['type'] == 'gold' for r in rewards)

def test_quest_stage_model(client):
    from app.core.models.quest import Quest, QuestStage
    quest = Quest(title='Stage Quest', description='Has stages')
    db.session.add(quest)
    db.session.commit()
    stage = QuestStage(quest_id=quest.id, description='Stage 1', objectives=[{'desc': 'Do X'}], completion_criteria={'type': 'all'}, order=1)
    db.session.add(stage)
    db.session.commit()
    fetched = QuestStage.query.filter_by(quest_id=quest.id).first()
    assert fetched is not None
    assert fetched.description == 'Stage 1'
    assert fetched.quest.id == quest.id
    # Test relationship
    assert quest.stages[0].description == 'Stage 1'


def test_quest_dependency_model(client):
    from app.core.models.quest import Quest, QuestDependency
    q1 = Quest(title='Q1', description='First')
    q2 = Quest(title='Q2', description='Second')
    db.session.add_all([q1, q2])
    db.session.commit()
    dep = QuestDependency(quest_id=q2.id, prerequisite_quest_id=q1.id)
    db.session.add(dep)
    db.session.commit()
    fetched = QuestDependency.query.filter_by(quest_id=q2.id).first()
    assert fetched is not None
    assert fetched.prerequisite_quest_id == q1.id
    # Test relationship
    assert fetched.quest.id == q2.id
    assert fetched.prerequisite_quest.id == q1.id


def test_quest_reward_model(client):
    from app.core.models.quest import Quest, QuestReward
    quest = Quest(title='Reward Quest', description='Has rewards')
    db.session.add(quest)
    db.session.commit()
    reward = QuestReward(quest_id=quest.id, reward_type='gold', value=100)
    db.session.add(reward)
    db.session.commit()
    fetched = QuestReward.query.filter_by(quest_id=quest.id).first()
    assert fetched is not None
    assert fetched.reward_type == 'gold'
    assert fetched.value == 100
    # Test relationship
    assert quest.rewards[0].reward_type == 'gold'


def test_quest_world_impact_model(client):
    from app.core.models.quest import Quest, QuestWorldImpact
    quest = Quest(title='Impact Quest', description='Has impact')
    db.session.add(quest)
    db.session.commit()
    impact = QuestWorldImpact(quest_id=quest.id, impact_type='faction', details={'faction_id': 1, 'change': 10})
    db.session.add(impact)
    db.session.commit()
    fetched = QuestWorldImpact.query.filter_by(quest_id=quest.id).first()
    assert fetched is not None
    assert fetched.impact_type == 'faction'
    assert fetched.details['change'] == 10
    # Test relationship
    assert quest.world_impacts[0].impact_type == 'faction'


def test_quest_model_edge_cases(client):
    from app.core.models.quest import QuestStage, QuestDependency, QuestReward, QuestWorldImpact
    # Missing required fields
    with pytest.raises(Exception):
        db.session.add(QuestStage())
        db.session.commit()
    db.session.rollback()
    # Invalid foreign key
    with pytest.raises(Exception):
        db.session.add(QuestDependency(quest_id=999, prerequisite_quest_id=888))
        db.session.commit()
    db.session.rollback()
    # Cascading delete
    from app.core.models.quest import Quest
    quest = Quest(title='Cascade Quest', description='Cascade test')
    db.session.add(quest)
    db.session.commit()
    stage = QuestStage(quest_id=quest.id, description='Stage', objectives=[], completion_criteria={}, order=1)
    db.session.add(stage)
    db.session.commit()
    db.session.delete(quest)
    db.session.commit()
    assert QuestStage.query.filter_by(quest_id=quest.id).count() == 0

def test_quest_service_methods(client):
    from app.services.quest_service import QuestService
    from app.core.models.quest import Quest, QuestStage
    service = QuestService(db.session)
    # Test create_quest
    quest_data = {'title': 'Service Quest', 'description': 'Service test'}
    quest = service.create_quest(quest_data)
    assert quest.id is not None
    # Test get_quest
    fetched = service.get_quest(quest.id)
    assert fetched is not None
    assert fetched.title == 'Service Quest'
    # Test get_all_quests
    all_quests = service.get_all_quests()
    assert any(q.id == quest.id for q in all_quests)
    # Test update_quest_stage
    stage = QuestStage(quest_id=quest.id, description='Stage', objectives=[], completion_criteria={'completed': False}, order=1)
    db.session.add(stage)
    db.session.commit()
    update = service.update_quest_stage(quest.id, stage.id, {'description': 'Updated Stage'})
    assert update is not None
    assert update.description == 'Updated Stage'
    # Test complete_quest_stage
    result = service.complete_quest_stage(quest.id, stage.id)
    assert result is True
    updated_stage = db.session.query(QuestStage).get(stage.id)
    assert updated_stage.completion_criteria.get('completed') is True
    # Test abandon_quest
    abandon = service.abandon_quest(quest.id)
    assert abandon is True
    abandoned_quest = service.get_quest(quest.id)
    assert abandoned_quest.status.name == 'FAILED'
    # Edge: update non-existent stage
    missing = service.update_quest_stage(quest.id, 9999, {'description': 'Nope'})
    assert missing is None
    # Edge: complete non-existent stage
    assert service.complete_quest_stage(quest.id, 9999) is False
    # Edge: abandon non-existent quest
    assert service.abandon_quest(9999) is False 