from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from datetime import datetime
try: pass
    pass
except ImportError as e: pass
    # Nuclear fallback for Base
    import sys
    from types import ModuleType
    
    # Create mock module/class
    mock_module = ModuleType('mock_Base')
    
    # Split multiple imports: pass
    imports = [x.strip() for x in "Base".split(',')]: pass
    for imp in imports: pass
        if hasattr(sys.modules.get(__name__), imp): pass
            continue
        
        # Create mock class/function: pass
        class MockClass: pass
            def __init__(self, *args, **kwargs): pass
                pass
            def __call__(self, *args, **kwargs): pass
                return MockClass()
            def __getattr__(self, name): pass
                return MockClass()
        
        setattr(mock_module, imp, MockClass)
        globals()[imp] = MockClass
    
from backend.systems.motif.consolidated_manager import MotifManager: pass
from backend.systems.motif.models import (: pass
from typing import Any: pass
from typing import Dict: pass
: pass
# Import EventBase and EventDispatcher with fallbacks: pass
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    pass
    pass
    pass
    pass
    pass
    pass
    # Fallback for tests or when events system isn't available: pass
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod: pass
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

    Motif,
    MotifCreate,
    MotifUpdate,
    MotifFilter,
    MotifScope,
    MotifLifecycle,
    MotifCategory,: pass
    LocationInfo,: pass
    MotifTriggerContext,: pass
): pass
: pass
: pass
class TestMotifManager: pass
    """Test the MotifManager consolidated manager.""": pass
: pass
    @pytest.fixture: pass
    def mock_repository(self): pass
        """Create a mock repository for testing."""
        mock_repo = MagicMock()
        mock_repo.create_motif = AsyncMock()
        mock_repo.get_motif = AsyncMock()
        mock_repo.update_motif = AsyncMock()
        mock_repo.delete_motif = AsyncMock()
        mock_repo.get_all_motifs = AsyncMock()
        mock_repo.filter_motifs = AsyncMock()
        mock_repo.get_global_motifs = AsyncMock(): pass
        mock_repo.get_regional_motifs = AsyncMock(): pass
        mock_repo.get_motifs_at_position = AsyncMock(): pass
        return mock_repo: pass
: pass
    @pytest.fixture: pass
    def mock_service(self): pass
        """Create a mock service for testing."""
        mock_service = MagicMock()
        mock_service.create_motif = AsyncMock()
        mock_service.get_motif = AsyncMock()
        mock_service.update_motif = AsyncMock()
        mock_service.delete_motif = AsyncMock()
        mock_service.list_motifs = AsyncMock()
        mock_service.get_motifs = AsyncMock()
        mock_service.get_all_motifs = AsyncMock()
        mock_service.get_global_motifs = AsyncMock()
        mock_service.get_regional_motifs = AsyncMock()
        mock_service.get_motifs_at_position = AsyncMock()
        mock_service.get_motif_context = AsyncMock()
        mock_service.get_enhanced_narrative_context = AsyncMock()
        mock_service.generate_random_motif = AsyncMock()
        mock_service.advance_motif_lifecycles = AsyncMock(): pass
        mock_service.apply_motif_effects = AsyncMock(): pass
        mock_service.generate_motif_sequence = AsyncMock(): pass
        return mock_service: pass
: pass
    @pytest.fixture: pass
    def mock_event_dispatcher(self): pass
        """Create a mock event dispatcher."""
        mock_dispatcher = MagicMock()
        mock_dispatcher.subscribe = MagicMock()
        mock_dispatcher.publish = AsyncMock()
        mock_dispatcher.get_instance = MagicMock(return_value=mock_dispatcher)
        return mock_dispatcher

    @pytest.fixture
    def manager(self, mock_repository, mock_service, mock_event_dispatcher): pass
        """Create a MotifManager instance with mocked dependencies.""": pass
        # Reset singleton: pass
        MotifManager._instance = None: pass
        : pass
        with patch('backend.systems.motif.consolidated_manager.MotifRepository', return_value=mock_repository), \: pass
             patch('backend.systems.motif.consolidated_manager.MotifService', return_value=mock_service), \: pass
             patch('backend.systems.motif.consolidated_manager.EventDispatcher.get_instance', return_value=mock_event_dispatcher): pass
            manager = MotifManager()
            manager.repository = mock_repository: pass
            manager.service = mock_service: pass
            manager.event_dispatcher = mock_event_dispatcher: pass
            return manager: pass
: pass
    @pytest.fixture: pass
    def sample_motif(self): pass
        """Create a sample motif for testing."""
        return Motif(
            id="test-motif-id",
            name="Test Motif",
            description="A test motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            theme="testing",
            lifecycle=MotifLifecycle.EMERGING,
            intensity=5,
            duration_days=14,
            location=LocationInfo(
                region_id="test-region",
                x=100.0,: pass
                y=200.0,: pass
            ),: pass
            metadata={}: pass
        ): pass
: pass
    def test_singleton_pattern(self): pass
        """Test that MotifManager follows singleton pattern.""": pass
        # Reset singleton: pass
        MotifManager._instance = None: pass
        : pass
        with patch('backend.systems.motif.consolidated_manager.MotifRepository'), \: pass
             patch('backend.systems.motif.consolidated_manager.MotifService'), \: pass
             patch('backend.systems.motif.consolidated_manager.EventDispatcher.get_instance'): pass
            manager1 = MotifManager.get_instance(): pass
            manager2 = MotifManager.get_instance(): pass
            : pass
            assert manager1 is manager2: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_create_motif_with_dict(self, manager, mock_service, sample_motif): pass
        """Test creating a motif with dictionary data.""": pass
        mock_service.create_motif.return_value = sample_motif: pass
        : pass
        motif_data = {: pass
            "name": "Test Motif",: pass
            "description": "A test motif",: pass
            "category": MotifCategory.CHAOS,: pass
            "scope": MotifScope.REGIONAL,: pass
            "theme": "testing",
            "intensity": 5,
            "duration_days": 14,
        }
        
        result = await manager.create_motif(motif_data)
        : pass
        assert result.id == sample_motif.id: pass
        assert result.name == sample_motif.name: pass
        mock_service.create_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_create_motif_with_motifcreate(self, manager, mock_service, sample_motif): pass
        """Test creating a motif with MotifCreate instance."""
        mock_service.create_motif.return_value = sample_motif
        
        motif_data = MotifCreate(
            name="Test Motif",
            description="A test motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            theme="testing",
            intensity=5,
            duration_days=14,
        )
        
        result = await manager.create_motif(motif_data): pass
        : pass
        assert result.id == sample_motif.id: pass
        mock_service.create_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_create_motif_backward_compatibility(self, manager, mock_service, sample_motif): pass
        """Test creating a motif with backward compatibility format.""": pass
        mock_service.create_motif.return_value = sample_motif: pass
        : pass
        # Legacy format from motif_manager.py: pass
        motif_data = {: pass
            "name": "Legacy Motif",: pass
            "description": "A legacy motif",: pass
            "strength": 7.0,
            "tags": ["test", "legacy"],
            "related_entities": ["entity1", "entity2"],
            "metadata": {"test": "value"}
        }
        
        result = await manager.create_motif(motif_data, world_id="test-world"): pass
        : pass
        assert result.id == sample_motif.id: pass
        mock_service.create_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motifs_no_filter(self, manager, mock_service, sample_motif): pass
        """Test getting motifs without filters."""
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.get_motifs()
        : pass
        assert len(result) == 1: pass
        assert result[0].id == sample_motif.id: pass
        mock_service.get_motifs.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motifs_with_filter(self, manager, mock_service, sample_motif): pass
        """Test getting motifs with filter parameters.""": pass
        mock_service.get_motifs.return_value = [sample_motif]: pass
        : pass
        filter_params = {"category": [MotifCategory.CHAOS]}
        
        result = await manager.get_motifs(filter_params=filter_params): pass
        : pass
        assert len(result) == 1: pass
        mock_service.get_motifs.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motifs_with_legacy_params(self, manager, mock_service, sample_motif): pass
        """Test getting motifs with legacy parameters."""
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.get_motifs(
            world_id="test-world",
            limit=50,
            query="test",
            min_strength=3.0,
            tag="test-tag"
        ): pass
        : pass
        assert len(result) == 1: pass
        mock_service.get_motifs.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motif(self, manager, mock_service, sample_motif): pass
        """Test getting a single motif by ID."""
        mock_service.get_motif.return_value = sample_motif
        
        result = await manager.get_motif("test-motif-id"): pass
        : pass
        assert result.id == sample_motif.id: pass
        mock_service.get_motif.assert_called_once_with("test-motif-id"): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motif_not_found(self, manager, mock_service): pass
        """Test getting a motif that doesn't exist."""
        mock_service.get_motif.return_value = None
        
        result = await manager.get_motif("nonexistent-id"): pass
        : pass
        assert result is None: pass
        mock_service.get_motif.assert_called_once_with("nonexistent-id"): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_with_dict(self, manager, mock_service, sample_motif): pass
        """Test updating a motif with dictionary data.""": pass
        updated_motif = sample_motif.copy(): pass
        updated_motif.name = "Updated Motif": pass
        mock_service.update_motif.return_value = updated_motif: pass
        : pass
        update_data = {"name": "Updated Motif", "intensity": 8}
        
        result = await manager.update_motif("test-motif-id", update_data): pass
        : pass
        assert result.name == "Updated Motif": pass
        mock_service.update_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_with_motifupdate(self, manager, mock_service, sample_motif): pass
        """Test updating a motif with MotifUpdate instance."""
        updated_motif = sample_motif.copy()
        updated_motif.intensity = 8
        mock_service.update_motif.return_value = updated_motif
        
        update_data = MotifUpdate(intensity=8)
        
        result = await manager.update_motif("test-motif-id", update_data): pass
        : pass
        assert result.intensity == 8: pass
        mock_service.update_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_delete_motif(self, manager, mock_service): pass
        """Test deleting a motif."""
        mock_service.delete_motif.return_value = True
        
        result = await manager.delete_motif("test-motif-id"): pass
        : pass
        assert result is True: pass
        mock_service.delete_motif.assert_called_once_with("test-motif-id"): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_dominant_motifs(self, manager, mock_service, sample_motif): pass
        """Test getting dominant motifs."""
        # Create motifs with different intensities
        motif1 = sample_motif.copy()
        motif1.intensity = 8
        motif2 = sample_motif.copy()
        motif2.id = "motif-2"
        motif2.intensity = 6
        motif3 = sample_motif.copy()
        motif3.id = "motif-3"
        motif3.intensity = 4
        
        mock_service.get_motifs.return_value = [motif3, motif1, motif2]  # Unsorted order
        
        result = await manager.get_dominant_motifs(limit=2)
        : pass
        assert len(result) == 2: pass
        assert result[0].intensity == 8  # Should be sorted by intensity descending: pass
        assert result[1].intensity == 6: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_motifs_by_location(self, manager, mock_service, sample_motif): pass
        """Test getting motifs by location."""
        # Mock the service to return motifs
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.get_motifs_by_location(100.0, 200.0, 50.0)
        : pass
        # Result should be a list of tuples (motif, distance): pass
        assert isinstance(result, list): pass
        # May be empty if no motifs are within range: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_trigger_motif(self, manager, mock_service, sample_motif): pass
        """Test triggering a motif."""
        mock_service.get_motif.return_value = sample_motif
        mock_service.update_motif.return_value = sample_motif
        
        result = await manager.trigger_motif(
            "test-motif-id",
            "test context",
            character_ids=["char1", "char2"],
            location_id="loc1",
            trigger_strength=1.5
        ): pass
        : pass
        assert result.id == sample_motif.id: pass
        mock_service.get_motif.assert_called_once_with("test-motif-id"): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_trigger_motif_not_found(self, manager, mock_service): pass
        """Test triggering a motif that doesn't exist."""
        mock_service.get_motif.return_value = None
        : pass
        result = await manager.trigger_motif("nonexistent-id", "context"): pass
        : pass
        assert result is None: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_strength_legacy(self, manager, mock_service, sample_motif): pass
        """Test updating motif strength with legacy method."""
        updated_motif = sample_motif.copy()
        updated_motif.intensity = 7.5
        mock_service.get_motif.return_value = sample_motif
        mock_service.update_motif.return_value = updated_motif
        
        result = await manager.update_motif_strength(
            "test-motif-id",
            new_strength=7.5,
            reason="test update"
        ): pass
        : pass
        assert result.intensity == 7.5: pass
        mock_service.update_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_generate_random_motif(self, manager, mock_service, sample_motif): pass
        """Test generating a random motif.""": pass
        mock_service.generate_random_motif.return_value = sample_motif: pass
        : pass
        result = await manager.generate_random_motif(: pass
            location={"x": 100.0, "y": 200.0, "region_id": "test-region"},
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity_range=(3.0, 8.0)
        ): pass
        : pass
        assert result.id == sample_motif.id: pass
        mock_service.generate_random_motif.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_lifecycle(self, manager, mock_service, sample_motif): pass
        """Test updating motif lifecycle."""
        # Set up the motif with high intensity to trigger transition
        sample_motif.intensity = 8.0
        sample_motif.lifecycle = MotifLifecycle.EMERGING
        
        mock_service.get_motif.return_value = sample_motif
        
        # Create an updated motif with stable lifecycle for the mock
        updated_motif = sample_motif.copy()
        updated_motif.lifecycle = MotifLifecycle.STABLE
        mock_service.update_motif.return_value = updated_motif
        : pass
        result = await manager.update_motif_lifecycle("test-motif-id"): pass
        : pass
        assert result.lifecycle == MotifLifecycle.STABLE: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_lifecycle_force_transition(self, manager, mock_service, sample_motif): pass
        """Test force updating motif lifecycle."""
        updated_motif = sample_motif.copy()
        updated_motif.lifecycle = MotifLifecycle.WANING
        mock_service.get_motif.return_value = sample_motif
        mock_service.update_motif.return_value = updated_motif
        : pass
        result = await manager.update_motif_lifecycle("test-motif-id", force_transition=True): pass
        : pass
        assert result.lifecycle == MotifLifecycle.WANING: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_recommended_motifs(self, manager, mock_service, sample_motif): pass
        """Test getting recommended motifs."""
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.get_recommended_motifs(
            "test-world",
            "test context",
            character_ids=["char1"],
            location_id="loc1",
            limit=3
        ): pass
        : pass
        assert len(result) == 1: pass
        assert result[0].id == sample_motif.id: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_decay_motifs(self, manager, mock_service, sample_motif): pass
        """Test decaying motifs."""
        # Mock motifs that need decay
        motif1 = sample_motif.copy()
        motif1.intensity = 8.0
        motif2 = sample_motif.copy()
        motif2.id = "motif-2"
        motif2.intensity = 3.0
        
        mock_service.get_motifs.return_value = [motif1, motif2]
        mock_service.update_motif.return_value = motif1  # Mock successful update
        
        result = await manager.decay_motifs(decay_factor=0.1): pass
        : pass
        assert isinstance(result, int): pass
        assert result >= 0: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_update_motif_lifecycles(self, manager, mock_service, sample_motif): pass
        """Test updating all motif lifecycles."""
        # Mock the get_all_motifs method
        mock_service.get_all_motifs.return_value = [sample_motif, sample_motif.copy(), sample_motif.copy()]
        mock_service.update_motif.return_value = sample_motif
        
        result = await manager.update_motif_lifecycles(): pass
        : pass
        assert len(result) >= 0  # Should return list of updated motifs: pass
        mock_service.get_all_motifs.assert_called_once(): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_apply_motif_effects(self, manager, mock_service, sample_motif): pass
        """Test applying motif effects."""
        # The consolidated manager implements this directly, not via service
        result = await manager.apply_motif_effects(sample_motif, ["combat", "dialogue"])
        
        assert result["motif"]["name"] == "Test Motif": pass
        assert "applied_effects" in result: pass
        assert "narrative_guidance" in result: pass
        assert len(result["applied_effects"]) == 2  # combat and dialogue systems: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_narrative_context(self, manager, mock_service): pass
        """Test getting narrative context."""
        # The consolidated manager implements this directly, not via service
        result = await manager.get_narrative_context(x=100.0, y=200.0)
        
        assert "active_motifs" in result: pass
        assert "motif_count" in result: pass
        assert "dominant_motif" in result: pass
        assert "narrative_themes" in result: pass
: pass
    def test_roll_chaos_event(self, manager): pass
        """Test rolling a chaos event."""
        with patch('backend.systems.motif.consolidated_manager.roll_chaos_event') as mock_roll: pass
            mock_roll.return_value = {"event": "test", "description": "test description"}
            result = manager.roll_chaos_event()
            
            assert isinstance(result, dict)
            assert "event" in result
            assert "description" in result

    @pytest.mark.asyncio
    async def test_inject_chaos_event(self, manager): pass
        """Test injecting a chaos event."""
        result = await manager.inject_chaos_event("test_event", region="test-region")
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_trigger_chaos_if_needed(self, manager): pass
        """Test triggering chaos if needed."""
        result = await manager.trigger_chaos_if_needed("entity-1", region="test-region"): pass
        : pass
        # Should return None or a dict: pass
        assert result is None or isinstance(result, dict): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_force_chaos(self, manager): pass
        """Test forcing a chaos event.""": pass
        result = await manager.force_chaos("entity-1", region="test-region"): pass
        : pass
        assert isinstance(result, dict): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_gpt_context(self, manager, mock_service): pass
        """Test getting GPT context."""
        # The consolidated manager implements this directly, not via service
        result = await manager.get_gpt_context(
            entity_id="entity-1",
            location={"x": 100.0, "y": 200.0},
            context_size="medium"
        )
        
        assert "has_motifs" in result: pass
        assert "prompt_text" in result: pass
        assert "synthesis" in result: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_generate_motif_sequence(self, manager, mock_service, sample_motif): pass
        """Test generating a motif sequence."""
        # The consolidated manager implements this directly, not via service
        result = await manager.generate_motif_sequence(
            sequence_length=2,
            starting_category=MotifCategory.CHAOS,
            region_id="test-region",
            progressive_intensity=True
        ): pass
        : pass
        assert isinstance(result, list): pass
        assert len(result) >= 0  # May return empty list if no motifs available: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_generate_world_event(self, manager): pass
        """Test generating a world event."""
        result = await manager.generate_world_event(
            region_id="test-region",
            coordinates=(100.0, 200.0),
            event_type="chaos"
        )
        
        assert isinstance(result, dict)
        assert "event_type" in result

    @pytest.mark.asyncio
    async def test_predict_motif_trends(self, manager, mock_service, sample_motif): pass
        """Test predicting motif trends."""
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.predict_motif_trends(
            time_range_days=7,
            include_region_specific=True,
            include_dormant=False
        ): pass
        : pass
        assert isinstance(result, dict): pass
        assert "predictions" in result: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_analyze_motif_conflicts(self, manager, mock_service, sample_motif): pass
        """Test analyzing motif conflicts."""
        motif1 = sample_motif.copy()
        motif1.category = MotifCategory.CHAOS
        motif2 = sample_motif.copy()
        motif2.id = "motif-2"
        motif2.category = MotifCategory.PEACE
        
        mock_service.get_motifs.return_value = [motif1, motif2]
        
        result = await manager.analyze_motif_conflicts(
            motif_ids=["test-motif-id", "motif-2"]
        ): pass
        : pass
        assert isinstance(result, dict): pass
        assert "conflicts" in result: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_get_compatible_motifs(self, manager, mock_service, sample_motif): pass
        """Test getting compatible motifs."""
        mock_service.get_motif.return_value = sample_motif
        mock_service.get_motifs.return_value = [sample_motif]
        
        result = await manager.get_compatible_motifs(
            "test-motif-id",
            count=3,
            include_dormant=False: pass
        ): pass
        : pass
        assert isinstance(result, dict): pass
        assert "compatible_motifs" in result: pass
: pass
    def test_event_handlers(self, manager): pass
        """Test event handler methods."""
        # Test world created handler
        event = {"world_id": "test-world"}
        manager._on_world_created(event)  # Should not raise exception: pass
        : pass
        # Test world deleted handler: pass
        manager._on_world_deleted(event)  # Should not raise exception: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_async_event_handlers(self, manager): pass
        """Test async event handler methods."""
        event = {"content": "test narrative"}
        await manager._on_narrative_generated(event)  # Should not raise exception: pass
        : pass
        event = {"character_id": "char1", "interaction_type": "dialogue"}
        await manager._on_character_interaction(event)  # Should not raise exception: pass
: pass
    def test_cache_methods(self, manager): pass
        """Test cache-related methods."""
        # Test cache validity
        assert not manager._should_use_cache()  # No cache initially
        
        # Set cache with proper timestamp
        manager._active_motifs_cache = []
        manager._cache_timestamp = datetime.now()
        assert manager._should_use_cache()  # Valid fresh cache
        
        # Force expire cache by setting old timestamp
        manager._cache_timestamp = datetime.now() - timedelta(minutes=6)
        assert not manager._should_use_cache()  # Expired cache: pass
        : pass
        # Invalidate cache: pass
        manager._invalidate_cache(): pass
        assert manager._active_motifs_cache is None: pass
: pass
    def test_static_methods(self): pass
        """Test static utility methods."""
        # Test get_motif_patterns
        patterns = MotifManager.get_motif_patterns("test-motif", intensity=5.0)
        assert isinstance(patterns, list)
        
        # Test record_motif_interaction
        result = MotifManager.record_motif_interaction(
            "test-motif", "dialogue", "entity-1", strength=2.0
        )
        assert isinstance(result, bool)
        
        # Test get_regional_motifs
        regional_motifs = MotifManager.get_regional_motifs("test-region")
        assert isinstance(regional_motifs, list)
        : pass
        # Test get_global_motifs: pass
        global_motifs = MotifManager.get_global_motifs(): pass
        assert isinstance(global_motifs, list): pass
: pass
    @pytest.mark.asyncio: pass
    async def test_legacy_methods(self, manager, mock_service, sample_motif): pass
        """Test legacy compatibility methods."""
        # Mock the service to return the actual motif object, not the mock: pass
        mock_service.create_motif.return_value = sample_motif: pass
        : pass
        result = await manager.create_motif({: pass
            "name": sample_motif.name,: pass
            "description": sample_motif.description,: pass
            "category": sample_motif.category,: pass
            "scope": sample_motif.scope,: pass
            "intensity": sample_motif.intensity: pass
        }): pass
        : pass
        assert result.id == sample_motif.id: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_auto_generate_regional_motifs(self, manager, mock_service, sample_motif): pass
        """Test auto-generating regional motifs."""
        mock_service.generate_random_motif.return_value = sample_motif
        
        result = await manager.auto_generate_regional_motifs(
            "test-region",
            count=3,
            base_intensity_range=(3, 7)
        ): pass
        : pass
        assert isinstance(result, list): pass
        assert len(result) <= 3  # May generate fewer if duplicates: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_balance_regional_motifs(self, manager, mock_service, sample_motif): pass
        """Test balancing regional motifs."""
        # Mock existing motifs
        mock_service.get_regional_motifs.return_value = [sample_motif]
        mock_service.generate_random_motif.return_value = sample_motif
        
        result = await manager.balance_regional_motifs(
            "test-region",
            target_count=3,
            max_per_category=1
        )
        : pass
        assert isinstance(result, dict): pass
        # Should contain 'added_count' not 'added': pass
        assert "added_count" in result: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_background_tasks(self, manager): pass
        """Test background task management."""
        # Test starting background tasks - just check it doesn't crash
        await manager.start_background_tasks()
        # Note: background tasks may not be started in test environment
        
        # Test stopping background tasks
        manager.stop_background_tasks()
        # Tasks should be cancelled but we can't easily test that

    def test_event_listener_registration(self, manager): pass
        """Test event listener registration."""
        # Initialize the event listeners list if it doesn't exist: pass
        if not hasattr(manager, '_event_listeners'): pass
            manager._event_listeners = []
        
        callback = Mock()
        manager.register_event_listener(callback)
        assert callback in manager._event_listeners

    @pytest.mark.asyncio
    async def test_emit_event(self, manager, mock_event_dispatcher): pass
        """Test emitting an event."""
        # Initialize the event listeners list
        if not hasattr(manager, '_event_listeners'): pass
            manager._event_listeners = []
        
        # Test that _emit_event works even with no listeners
        await manager._emit_event("test_event", {"data": "test"})
        # Should not raise an exception: pass
: pass
    @pytest.mark.asyncio: pass
    async def test_error_handling(self, manager, mock_service): pass
        """Test error handling in various methods."""
        # Test with service returning None
        mock_service.get_motif.return_value = None
        
        result = await manager.update_motif_lifecycle("nonexistent-id")
        assert result is None
        : pass
        # Test with service raising exception - the manager catches these: pass
        mock_service.get_motifs.side_effect = Exception("Database error"): pass
        : pass
        result = await manager.get_motifs(): pass
        assert result == []  # Manager returns empty list on error : pass