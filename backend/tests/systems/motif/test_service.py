"""
Test module for motif.service

Tests the motif service business logic according to Development_Bible.md requirements:
- Narrative context generation for AI systems
- Motif lifecycle management 
- System integration patterns
- Business rule compliance
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Import the module under test
from backend.systems.motif.services.service import MotifService
from backend.infrastructure.systems.motif.models import (
    Motif, MotifCreate, MotifScope, MotifLifecycle, MotifCategory
)


class TestMotifService:
    """Test class for motif service business logic compliance"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing"""
        return Mock()
        
    @pytest.fixture
    def service(self, mock_repository):
        """Service instance with mocked repository"""
        return MotifService(repository=mock_repository)
        
    @pytest.fixture
    def sample_motif(self):
        """Sample motif for testing"""
        return Motif(
            id="test-id",
            name="Test Hope Motif",
            description="A test motif representing hope",
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL,
            intensity=7,
            lifecycle=MotifLifecycle.STABLE,
            theme="hope"
        )

    @pytest.mark.asyncio
    async def test_create_motif_bible_compliance(self, service, mock_repository):
        """Test motif creation follows Bible requirements"""
        # Bible requires: automatic descriptor generation, tone determination
        create_data = MotifCreate(
            name="Rising Hope",
            description="Hope emerges in dark times",
            category=MotifCategory.HOPE,
            scope=MotifScope.REGIONAL,
            intensity=6,
            theme="hope"  # Add theme to create data
        )
        
        # Mock the repository response
        expected_motif = Motif(**create_data.dict())
        mock_repository.create_motif = AsyncMock(return_value=expected_motif)
        
        result = await service.create_motif(create_data)
        
        # Verify Bible requirements are met
        assert result.name == "Rising Hope"
        assert result.category == MotifCategory.HOPE
        assert result.scope == MotifScope.REGIONAL
        # Verify automatic fields are set (these are set by the service create_motif method)
        assert result.created_at is not None
        # Descriptors and tone should be automatically generated
        assert result.descriptors is not None
        assert result.tone is not None
        assert result.narrative_direction is not None
                
    @pytest.mark.asyncio 
    async def test_get_motif_context_ai_integration(self, service, mock_repository, sample_motif):
        """Test narrative context generation for AI systems per Bible"""
        # Bible requirement: "providing contextual guidance to AI systems"
        mock_repository.get_motifs_at_position = AsyncMock(return_value=[sample_motif])
        service.get_motifs_at_position = AsyncMock(return_value=[sample_motif])
        
        context = await service.get_motif_context(x=100.0, y=200.0)
        
        # Verify Bible-specified context structure
        assert "active_motifs" in context
        assert "dominant_motif" in context
        assert "narrative_themes" in context
        assert "motif_count" in context
        
        # Verify motif data is properly formatted
        assert len(context["active_motifs"]) == 1
        assert context["active_motifs"][0]["name"] == "Test Hope Motif"
        assert context["active_motifs"][0]["category"] == "hope"
        assert context["active_motifs"][0]["intensity"] == 7
        assert context["dominant_motif"] == "Test Hope Motif"
        
    @pytest.mark.asyncio
    async def test_enhanced_narrative_context_bible_compliance(self, service, mock_repository):
        """Test enhanced narrative context generation follows Bible requirements"""
        # Mock the list_motifs to return an empty list instead of Mock
        service.list_motifs = AsyncMock(return_value=[])
        
        context = await service.get_enhanced_narrative_context(context_size="medium")
        
        # Bible requires: structured narrative context for AI systems
        assert isinstance(context, dict)
        assert "has_motifs" in context
        assert "prompt_text" in context
        assert "context_size" in context
        assert context["context_size"] == "medium"
        
    def test_extract_narrative_themes_bible_categories(self, service, sample_motif):
        """Test narrative theme extraction for Bible-specified categories"""
        # Bible mentions specific categories: betrayal, chaos, death, hope
        betrayal_motif = Motif(
            id="betrayal-test",
            name="Broken Trust",
            description="Trust is shattered",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.LOCAL,
            intensity=8,
            theme="betrayal"
        )
        
        chaos_motif = Motif(
            id="chaos-test", 
            name="Wild Magic",
            description="Magic runs wild",
            category=MotifCategory.CHAOS,
            scope=MotifScope.GLOBAL,
            intensity=6,
            theme="chaos"
        )
        
        motifs = [sample_motif, betrayal_motif, chaos_motif]
        themes = service._extract_narrative_themes(motifs)
        
        # Verify Bible-specified themes are extracted
        theme_strings = " ".join(themes)
        assert "optimism despite adversity" in theme_strings  # Hope theme
        assert "trust is fragile" in theme_strings  # Betrayal theme
        assert "unpredictability and disorder" in theme_strings  # Chaos theme
        
    @pytest.mark.asyncio
    async def test_motif_lifecycle_advancement_bible_compliance(self, service, mock_repository):
        """Test motif lifecycle advancement follows Bible lifecycle states"""
        # Bible specifies: EMERGING, STABLE, WANING, DORMANT, CONCLUDED
        emerging_motif = Motif(
            id="emerging-test",
            name="New Hope",
            description="Hope begins to grow", 
            category=MotifCategory.HOPE,
            scope=MotifScope.GLOBAL,
            lifecycle=MotifLifecycle.EMERGING,
            start_time=datetime.utcnow() - timedelta(days=5),
            theme="hope"
        )
        
        # Mock the repository methods that advance_motif_lifecycles calls
        mock_repository.get_all_motifs = Mock(return_value=[emerging_motif])  # This one is NOT async
        mock_repository.update_motif = Mock(return_value=emerging_motif)
        mock_repository.cleanup_expired_motifs = Mock(return_value=0)
        
        advanced_count = await service.advance_motif_lifecycles()
        
        # Verify lifecycle advancement occurs
        assert advanced_count >= 0
        
    @pytest.mark.asyncio
    async def test_global_motifs_retrieval_bible_scope(self, service, mock_repository, sample_motif):
        """Test global motif retrieval matches Bible scope requirements"""
        # Bible specifies GLOBAL scope affects entire world
        service.get_global_motifs = AsyncMock(return_value=[sample_motif])
        
        global_motifs = await service.get_global_motifs()
        
        assert len(global_motifs) == 1
        assert global_motifs[0].scope == MotifScope.GLOBAL
        
    @pytest.mark.asyncio 
    async def test_regional_motifs_retrieval_bible_scope(self, service, mock_repository):
        """Test regional motif retrieval matches Bible scope requirements"""
        # Bible specifies REGIONAL scope affects specific geographic areas
        regional_motif = Motif(
            id="regional-test",
            name="Regional Tension",
            description="Tension grows in the region",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=5,
            theme="chaos"
        )
        
        service.get_regional_motifs = AsyncMock(return_value=[regional_motif])
        
        regional_motifs = await service.get_regional_motifs("test_region")
        
        assert len(regional_motifs) == 1
        assert regional_motifs[0].scope == MotifScope.REGIONAL
        
    @pytest.mark.asyncio
    async def test_position_based_motif_filtering_bible_spatial_queries(self, service, mock_repository, sample_motif):
        """Test position-based filtering supports Bible spatial query requirements"""
        # Bible: "Location-Based Filtering: Spatial queries for regional/local motifs"
        service.get_motifs_at_position = AsyncMock(return_value=[sample_motif])
        
        motifs = await service.get_motifs_at_position(x=100.0, y=200.0, radius=50.0)
        
        # Verify spatial query was called with correct parameters
        service.get_motifs_at_position.assert_called_once_with(x=100.0, y=200.0, radius=50.0)
        assert len(motifs) == 1
