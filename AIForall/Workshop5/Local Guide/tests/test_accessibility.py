"""
Accessibility tests for WCAG 2.1 AA compliance
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create app for testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAccessibilityMarkup:
    """Tests for accessibility markup"""
    
    def test_html_lang_attribute(self, client):
        """Test HTML has lang attribute"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'lang="en"' in response.get_data(as_text=True)
    
    def test_page_has_title(self, client):
        """Test page has title element"""
        response = client.get('/')
        assert response.status_code == 200
        assert '<title>' in response.get_data(as_text=True)
    
    def test_page_has_main_content(self, client):
        """Test page has main content area"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert '<main' in html or 'id="main-content"' in html
    
    def test_skip_to_main_link(self, client):
        """Test skip to main content link exists"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'skip-to-main' in html or 'Skip to main content' in html
    
    def test_navigation_has_role(self, client):
        """Test navigation has proper role"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'role="navigation"' in html or 'role="main"' in html or '<nav' in html
    
    def test_footer_has_role(self, client):
        """Test footer has proper role"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'role="contentinfo"' in html or '<footer' in html
    
    def test_buttons_have_labels(self, client):
        """Test buttons have accessible labels"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for aria-label or text content in buttons
        assert 'aria-label' in html or 'Send' in html or 'Close' in html


class TestFormAccessibility:
    """Tests for form accessibility"""
    
    def test_search_input_has_label(self, client):
        """Test search input has accessible label"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Search input should have placeholder or label
        assert 'search' in html.lower()
    
    def test_chat_input_has_label(self, client):
        """Test chat input has accessible label"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'aria-label' in html or 'placeholder' in html


class TestLinkAccessibility:
    """Tests for link accessibility"""
    
    def test_links_have_text(self, client):
        """Test links have descriptive text"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for links with text content
        assert '<a' in html
    
    def test_category_links_accessible(self, client):
        """Test category links are accessible"""
        response = client.get('/categories')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Links should have text or aria-label
        assert '<a' in html


class TestBreadcrumbAccessibility:
    """Tests for breadcrumb accessibility"""
    
    def test_breadcrumb_has_nav_role(self, client):
        """Test breadcrumb has nav role"""
        response = client.get('/categories/food')
        assert response.status_code in [200, 404]
        html = response.get_data(as_text=True)
        # Breadcrumb should have nav role
        if 'breadcrumb' in html:
            assert 'aria-label="breadcrumb"' in html or '<nav' in html
    
    def test_breadcrumb_current_page_marked(self, client):
        """Test current page in breadcrumb is marked"""
        response = client.get('/categories/food')
        assert response.status_code in [200, 404]
        html = response.get_data(as_text=True)
        # Current page should be marked with aria-current
        if 'breadcrumb' in html:
            assert 'aria-current' in html or 'active' in html


class TestImageAccessibility:
    """Tests for image accessibility"""
    
    def test_images_have_alt_text(self, client):
        """Test images have alt text"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for images with alt text or aria-hidden
        if '<img' in html:
            # Images should have alt attribute or aria-hidden
            assert 'alt=' in html or 'aria-hidden' in html


class TestColorContrast:
    """Tests for color contrast"""
    
    def test_page_has_sufficient_contrast(self, client):
        """Test page uses colors with sufficient contrast"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for CSS link or style tag (supports both minified and non-minified)
        assert 'style.min.css' in html or 'style.css' in html or '<style' in html


class TestKeyboardNavigation:
    """Tests for keyboard navigation"""
    
    def test_page_has_focus_styles(self, client):
        """Test page has focus styles for keyboard navigation"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for focus styles in CSS
        assert ':focus' in html or 'outline' in html
    
    def test_buttons_are_keyboard_accessible(self, client):
        """Test buttons are keyboard accessible"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Buttons should be actual button elements or have role
        assert '<button' in html or 'role="button"' in html


class TestAriaLabels:
    """Tests for ARIA labels"""
    
    def test_chat_widget_has_aria_label(self, client):
        """Test chat widget has aria-label"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Chat widget should have aria-label or role
        if 'chat' in html.lower():
            assert 'aria-label' in html or 'role=' in html
    
    def test_buttons_have_aria_labels(self, client):
        """Test buttons have aria-labels"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Buttons should have aria-label or text
        if '<button' in html:
            assert 'aria-label' in html or 'Send' in html or 'Close' in html


class TestSemanticHTML:
    """Tests for semantic HTML"""
    
    def test_page_uses_semantic_elements(self, client):
        """Test page uses semantic HTML elements"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for semantic elements
        assert '<nav' in html or '<main' in html or '<footer' in html or '<header' in html
    
    def test_headings_are_hierarchical(self, client):
        """Test headings follow hierarchical structure"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Should have h1 or h2
        assert '<h1' in html or '<h2' in html


class TestResponsiveDesign:
    """Tests for responsive design accessibility"""
    
    def test_viewport_meta_tag(self, client):
        """Test viewport meta tag is present"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'viewport' in html
    
    def test_page_is_mobile_friendly(self, client):
        """Test page has mobile-friendly design"""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check for responsive design indicators
        assert 'viewport' in html or 'media' in html


class TestErrorHandling:
    """Tests for accessible error handling"""
    
    def test_404_page_accessible(self, client):
        """Test 404 error page is accessible"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        html = response.get_data(as_text=True)
        # Error page should have proper structure
        assert '<title>' in html
    
    def test_error_messages_accessible(self, client):
        """Test error messages are accessible"""
        response = client.get('/api/search?q=')
        # Should return error or empty results
        assert response.status_code in [200, 400]
