"""
Frontend Performance Optimization Tests

Tests for minified CSS/JS and lazy loading implementation.
"""

import os
import pytest
from pathlib import Path


class TestMinifiedAssets:
    """Test minified CSS and JavaScript files"""
    
    def test_minified_css_exists(self):
        """Test that minified CSS file exists"""
        css_path = Path('static/css/style.min.css')
        assert css_path.exists(), "Minified CSS file not found"
    
    def test_minified_js_main_exists(self):
        """Test that minified main JS file exists"""
        js_path = Path('static/js/main.min.js')
        assert js_path.exists(), "Minified main JS file not found"
    
    def test_minified_js_chat_exists(self):
        """Test that minified chat JS file exists"""
        js_path = Path('static/js/chat.min.js')
        assert js_path.exists(), "Minified chat JS file not found"
    
    def test_lazy_load_script_exists(self):
        """Test that lazy load script exists"""
        js_path = Path('static/js/lazy-load.min.js')
        assert js_path.exists(), "Lazy load script not found"
    
    def test_minified_css_is_smaller(self):
        """Test that minified CSS is smaller than original"""
        original_size = os.path.getsize('static/css/style.css')
        minified_size = os.path.getsize('static/css/style.min.css')
        
        # Minified should be at least 30% smaller
        reduction = (original_size - minified_size) / original_size
        assert reduction >= 0.30, f"CSS reduction only {reduction*100:.1f}%, expected >= 30%"
    
    def test_minified_js_main_is_smaller(self):
        """Test that minified main JS is smaller than original"""
        original_size = os.path.getsize('static/js/main.js')
        minified_size = os.path.getsize('static/js/main.min.js')
        
        # Minified should be at least 30% smaller
        reduction = (original_size - minified_size) / original_size
        assert reduction >= 0.30, f"JS reduction only {reduction*100:.1f}%, expected >= 30%"
    
    def test_minified_js_chat_is_smaller(self):
        """Test that minified chat JS is smaller than original"""
        original_size = os.path.getsize('static/js/chat.js')
        minified_size = os.path.getsize('static/js/chat.min.js')
        
        # Minified should be at least 30% smaller
        reduction = (original_size - minified_size) / original_size
        assert reduction >= 0.30, f"Chat JS reduction only {reduction*100:.1f}%, expected >= 30%"
    
    def test_minified_css_valid_syntax(self):
        """Test that minified CSS has valid syntax"""
        with open('static/css/style.min.css', 'r') as f:
            content = f.read()
        
        # Check for basic CSS structure
        assert '{' in content, "Minified CSS missing opening braces"
        assert '}' in content, "Minified CSS missing closing braces"
        assert ':' in content, "Minified CSS missing colons"
        
        # Count braces - should be balanced
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, "Unbalanced braces in minified CSS"
    
    def test_minified_js_valid_syntax(self):
        """Test that minified JS has valid syntax"""
        with open('static/js/main.min.js', 'r') as f:
            content = f.read()
        
        # Check for basic JS structure
        assert 'function' in content or 'const' in content or '=>' in content, \
            "Minified JS missing function definitions"
        
        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, "Unbalanced parentheses in minified JS"
    
    def test_minified_chat_js_valid_syntax(self):
        """Test that minified chat JS has valid syntax"""
        with open('static/js/chat.min.js', 'r') as f:
            content = f.read()
        
        # Check for class definition
        assert 'class ChatInterface' in content, "ChatInterface class not found in minified chat JS"
        
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, "Unbalanced braces in minified chat JS"


class TestLazyLoading:
    """Test lazy loading implementation"""
    
    def test_lazy_load_script_exists(self):
        """Test that lazy load script exists"""
        js_path = Path('static/js/lazy-load.min.js')
        assert js_path.exists(), "Lazy load script not found"
    
    def test_lazy_load_script_has_intersection_observer(self):
        """Test that lazy load script uses IntersectionObserver"""
        with open('static/js/lazy-load.min.js', 'r') as f:
            content = f.read()
        
        assert 'IntersectionObserver' in content, \
            "Lazy load script missing IntersectionObserver"
    
    def test_lazy_load_script_handles_data_src(self):
        """Test that lazy load script handles data-src attribute"""
        with open('static/js/lazy-load.min.js', 'r') as f:
            content = f.read()
        
        assert 'data-src' in content, "Lazy load script missing data-src handling"
    
    def test_lazy_load_script_handles_images(self):
        """Test that lazy load script handles images"""
        with open('static/js/lazy-load.min.js', 'r') as f:
            content = f.read()
        
        assert 'IMG' in content, "Lazy load script missing IMG tag handling"
    
    def test_lazy_load_script_handles_iframes(self):
        """Test that lazy load script handles iframes"""
        with open('static/js/lazy-load.min.js', 'r') as f:
            content = f.read()
        
        assert 'IFRAME' in content, "Lazy load script missing IFRAME tag handling"
    
    def test_lazy_load_script_has_fallback(self):
        """Test that lazy load script has fallback for older browsers"""
        with open('static/js/lazy-load.min.js', 'r') as f:
            content = f.read()
        
        # Should have else clause for browsers without IntersectionObserver
        assert 'else' in content, "Lazy load script missing fallback for older browsers"


class TestBaseTemplateOptimization:
    """Test that base template uses optimized assets"""
    
    def test_base_template_uses_minified_css(self):
        """Test that base template uses minified CSS"""
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'style.min.css' in content, "Base template not using minified CSS"
    
    def test_base_template_uses_minified_js(self):
        """Test that base template uses minified JS"""
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'main.min.js' in content, "Base template not using minified main JS"
        assert 'chat.min.js' in content, "Base template not using minified chat JS"
    
    def test_base_template_includes_lazy_load(self):
        """Test that base template includes lazy load script"""
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'lazy-load.min.js' in content, "Base template not including lazy load script"
    
    def test_base_template_lazy_load_loads_first(self):
        """Test that lazy load script loads before other scripts"""
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        lazy_load_pos = content.find('lazy-load.min.js')
        main_js_pos = content.find('main.min.js')
        
        assert lazy_load_pos < main_js_pos, \
            "Lazy load script should load before main JS"


class TestAssetSizes:
    """Test asset file sizes and compression"""
    
    def test_minified_css_size(self):
        """Test minified CSS file size"""
        size = os.path.getsize('static/css/style.min.css')
        # Should be less than 10KB
        assert size < 10000, f"Minified CSS too large: {size} bytes"
    
    def test_minified_main_js_size(self):
        """Test minified main JS file size"""
        size = os.path.getsize('static/js/main.min.js')
        # Should be less than 5KB
        assert size < 5000, f"Minified main JS too large: {size} bytes"
    
    def test_minified_chat_js_size(self):
        """Test minified chat JS file size"""
        size = os.path.getsize('static/js/chat.min.js')
        # Should be less than 5KB
        assert size < 5000, f"Minified chat JS too large: {size} bytes"
    
    def test_lazy_load_script_size(self):
        """Test lazy load script file size"""
        size = os.path.getsize('static/js/lazy-load.min.js')
        # Should be less than 2KB
        assert size < 2000, f"Lazy load script too large: {size} bytes"
    
    def test_total_asset_reduction(self):
        """Test total asset size reduction"""
        original_css = os.path.getsize('static/css/style.css')
        original_main_js = os.path.getsize('static/js/main.js')
        original_chat_js = os.path.getsize('static/js/chat.js')
        original_total = original_css + original_main_js + original_chat_js
        
        minified_css = os.path.getsize('static/css/style.min.css')
        minified_main_js = os.path.getsize('static/js/main.min.js')
        minified_chat_js = os.path.getsize('static/js/chat.min.js')
        minified_total = minified_css + minified_main_js + minified_chat_js
        
        reduction = (original_total - minified_total) / original_total
        # Should achieve at least 35% reduction
        assert reduction >= 0.35, \
            f"Total reduction only {reduction*100:.1f}%, expected >= 35%"


class TestPerformanceImpact:
    """Test performance impact of optimizations"""
    
    def test_minified_assets_load_faster(self):
        """Test that minified assets are smaller and load faster"""
        original_total = (
            os.path.getsize('static/css/style.css') +
            os.path.getsize('static/js/main.js') +
            os.path.getsize('static/js/chat.js')
        )
        
        minified_total = (
            os.path.getsize('static/css/style.min.css') +
            os.path.getsize('static/js/main.min.js') +
            os.path.getsize('static/js/chat.min.js')
        )
        
        # Minified should be significantly smaller
        assert minified_total < original_total * 0.65, \
            "Minified assets not small enough"
    
    def test_lazy_load_reduces_initial_load(self):
        """Test that lazy loading reduces initial page load"""
        # Lazy load script is small and defers image loading
        lazy_load_size = os.path.getsize('static/js/lazy-load.min.js')
        
        # Should be very small (< 2KB)
        assert lazy_load_size < 2000, \
            "Lazy load script too large to be effective"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
