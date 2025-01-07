"""Routes for HTML pages"""
from flask import Blueprint, render_template

def create_page_routes():
    """Factory function to create page routes blueprint"""
    page_routes = Blueprint('pages', __name__)

    @page_routes.route('/')
    def index():
        """Render the main page"""
        return render_template('html/index.html')

    @page_routes.route('/about')
    def about():
        """Render the about page"""
        return render_template('html/about.html')

    @page_routes.route('/error/404')
    def error_404():
        """Render 404 error page"""
        return render_template('html/404.html'), 404

    @page_routes.route('/error/500')
    def error_500():
        """Render 500 error page"""
        return render_template('html/500.html'), 500

    @page_routes.errorhandler(404)
    def not_found_error():
        """Handle 404 errors"""
        return render_template('html/404.html'), 404

    @page_routes.errorhandler(500)
    def internal_error():
        """Handle 500 errors"""
        return render_template('html/500.html'), 500

    return page_routes
