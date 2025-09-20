# Test Command

## Usage
`/test <COMPONENT_OR_FEATURE>`

## Context
Create and run comprehensive tests for: $ARGUMENTS

## Automatic Integrations
- 🎯 Tests linked to requirements automatically
- 📊 Coverage metrics sent to dashboard
- 📦 GitHub commit after successful tests
- 🧠 Test results saved to memory

## Process

### 0. Pre-Test Setup (Automatic)
```bash
# Auto-executes:
# Start dashboard if needed
.claude-workspace/services/dashboard/dashboard.sh start
# Check which requirements need tests
python -c "from .claude-workspace.shared.parsers.requirements_parser import RequirementsParser; parser = RequirementsParser('$PROJECT_PATH'); print(parser.scan_tests())"
```

### 1. Test Planning
- Identify test scenarios
- Define test boundaries
- Create test data requirements
- Plan test execution order

### 2. Unit Tests
Write focused unit tests:
```python
import pytest
from unittest.mock import Mock, patch
from src.rss_plex_manager.services import ExampleService


class TestExampleService:
    """Test suite for ExampleService.
    
    Tests for REQ-001, REQ-002  # ← Link tests to requirements
    """
    
    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies."""
        mock_dependency = Mock()
        return ExampleService(mock_dependency)
    
    @pytest.fixture
    def sample_data(self):
        """Provide sample test data."""
        return {
            "field": "test_value",
            "optional_field": 42
        }
    
    async def test_process_success(self, service, sample_data):
        """Test successful processing."""
        # Arrange
        expected_result = {"status": "success"}
        service.dependency.process.return_value = expected_result
        
        # Act
        result = await service.process(sample_data)
        
        # Assert
        assert result == expected_result
        service.dependency.process.assert_called_once_with(sample_data)
    
    async def test_process_validation_error(self, service):
        """Test validation error handling."""
        # Arrange
        invalid_data = {"invalid": "data"}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.process(invalid_data)
        
        assert "field required" in str(exc_info.value)
    
    @pytest.mark.parametrize("input_value,expected", [
        ("test1", {"result": "processed_test1"}),
        ("test2", {"result": "processed_test2"}),
        ("", {"result": "processed_empty"}),
    ])
    async def test_process_various_inputs(self, service, input_value, expected):
        """Test processing with various inputs."""
        data = {"field": input_value}
        service.dependency.process.return_value = expected
        
        result = await service.process(data)
        
        assert result == expected
```

### 3. Integration Tests
Test component interactions:
```python
import pytest
from fastapi.testclient import TestClient
from src.rss_plex_manager.web.app import app


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Provide authentication headers."""
        return {"Authorization": "Bearer test_token"}
    
    def test_create_resource(self, client, auth_headers):
        """Test resource creation flow."""
        # Arrange
        payload = {
            "name": "Test Resource",
            "description": "Test description"
        }
        
        # Act
        response = client.post(
            "/api/v1/resources",
            json=payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert "id" in data
    
    def test_get_resource(self, client, auth_headers):
        """Test resource retrieval."""
        # Create resource first
        create_response = client.post(
            "/api/v1/resources",
            json={"name": "Test"},
            headers=auth_headers
        )
        resource_id = create_response.json()["id"]
        
        # Get resource
        get_response = client.get(
            f"/api/v1/resources/{resource_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        assert get_response.json()["id"] == resource_id
```

### 4. End-to-End Tests
Test complete workflows:
```python
import pytest
import asyncio
from src.rss_plex_manager.services import RSSProcessor, PlexOrganizer


class TestE2EWorkflow:
    """End-to-end workflow tests."""
    
    @pytest.fixture
    async def setup_services(self):
        """Setup required services."""
        rss_processor = RSSProcessor()
        plex_organizer = PlexOrganizer()
        yield rss_processor, plex_organizer
        # Cleanup
        await rss_processor.cleanup()
        await plex_organizer.cleanup()
    
    async def test_complete_rss_to_plex_flow(self, setup_services):
        """Test complete RSS to Plex workflow."""
        rss_processor, plex_organizer = setup_services
        
        # Step 1: Process RSS feed
        feed_url = "https://example.com/feed.xml"
        items = await rss_processor.fetch_and_parse(feed_url)
        assert len(items) > 0
        
        # Step 2: Filter content
        filtered_items = await rss_processor.filter_items(
            items,
            criteria={"quality": "1080p"}
        )
        assert len(filtered_items) <= len(items)
        
        # Step 3: Download content
        downloads = []
        for item in filtered_items[:1]:  # Test with first item
            download = await rss_processor.download_content(item)
            downloads.append(download)
        
        # Step 4: Organize in Plex
        for download in downloads:
            result = await plex_organizer.organize_media(download)
            assert result["status"] == "organized"
            assert "plex_path" in result
```

### 5. Test Fixtures & Utilities
Create reusable test utilities:
```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Provide test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    with patch("redis.Redis") as mock:
        yield mock
```

### 6. Test Execution & Coverage
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/rss_plex_manager --cov-report=html

# Run specific test file
pytest tests/test_services.py

# Run tests matching pattern
pytest -k "test_process"

# Run with verbose output
pytest -v

# Run with markers
pytest -m "slow"
```

## Test Categories

### Unit Tests
- Isolated component testing
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests
- Component interaction testing
- Use test database
- API endpoint testing
- Medium execution time

### E2E Tests
- Complete workflow testing
- Real-world scenarios
- Slower execution
- Critical path coverage

### Performance Tests
- Load testing
- Response time validation
- Resource usage monitoring
- Scalability verification

## Quality Gates
- [ ] 80% code coverage minimum
- [ ] All tests passing
- [ ] No flaky tests
- [ ] Test execution < 5 minutes
- [ ] Clear test documentation
- [ ] Proper test isolation
- [ ] Requirements referenced in tests
- [ ] Coverage metrics in dashboard

## Post-Test Hooks (Automatic)
```bash
# These run automatically after tests:

# 1. Update requirements coverage
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH

# 2. Send coverage to dashboard
coverage_percent=$(pytest --cov=src --cov-report=term | grep TOTAL | awk '{print $4}')
curl -X POST http://localhost:8080/api/metrics \
  -H "Content-Type: application/json" \
  -d '{"test_coverage": "'$coverage_percent'", "project": "$PROJECT_NAME"}'

# 3. Git commit
git add .
git commit -m "test: added tests for $ARGUMENTS"

# 4. Update requirements status
sqlite3 .claude-project/metrics/requirements.db \
  "UPDATE requirement_status SET coverage_percent = '$coverage_percent' WHERE id IN (SELECT requirement_id FROM test_files WHERE file_path LIKE '%$ARGUMENTS%')"
```
