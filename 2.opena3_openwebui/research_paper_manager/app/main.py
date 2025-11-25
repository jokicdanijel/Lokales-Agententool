"""
Main Flask Application - Research Paper Manager
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
import json

# Import models and services
from app.models.paper import Base, Paper, Tag, Collection, CollectionPaper
from app.services.arxiv_service import ArxivService
from app.db.database import init_db, get_session

# Initialize Flask App
app = Flask(__name__, template_folder='../web', static_folder='../web')
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
DB_PATH = os.getenv('DB_PATH', './research_papers.db')

# Initialize Database
init_db(DB_PATH)

# Initialize Services
arxiv_service = ArxivService()


# ============================================================================
# Health & Status Routes
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Research Paper Manager',
        'version': '0.1.0',
        'timestamp': __import__('datetime').datetime.utcnow().isoformat()
    }), 200


@app.route('/api/status', methods=['GET'])
def status():
    """Detailed status"""
    session = get_session()
    try:
        paper_count = session.query(Paper).count()
        collection_count = session.query(Collection).count()
        tag_count = session.query(Tag).count()

        return jsonify({
            'status': 'operational',
            'database': {
                'papers': paper_count,
                'collections': collection_count,
                'tags': tag_count
            },
            'features': {
                'arxiv_integration': True,
                'ai_features': True,
                'search': True,
                'tagging': True
            }
        }), 200
    finally:
        session.close()


# ============================================================================
# Paper Routes
# ============================================================================

@app.route('/api/papers', methods=['GET'])
def list_papers():
    """Get all papers with pagination"""
    session = get_session()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = session.query(Paper)
        total = query.count()

        papers = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'data': [p.to_dict() for p in papers],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
    finally:
        session.close()


@app.route('/api/papers/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """Get single paper"""
    session = get_session()
    try:
        paper = session.query(Paper).filter_by(id=paper_id).first()

        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        paper_data = paper.to_dict()
        paper_data['tags'] = [t.tag_name for t in paper.tags]

        return jsonify(paper_data), 200
    finally:
        session.close()


@app.route('/api/papers', methods=['POST'])
def create_paper():
    """Create new paper"""
    session = get_session()
    try:
        data = request.get_json()

        # Validierung
        if not data.get('title') or not data.get('authors'):
            return jsonify({'error': 'Missing required fields'}), 400

        paper = Paper(
            arxiv_id=data.get('arxiv_id'),
            title=data['title'],
            authors=data['authors'],
            abstract=data.get('abstract'),
            category=data.get('category'),
            url=data.get('url'),
            pdf_url=data.get('pdf_url'),
            published_date=data.get('published_date'),
            summary=data.get('summary'),
            keywords=data.get('keywords'),
            metadata=data.get('metadata', {})
        )

        session.add(paper)
        session.commit()

        return jsonify(paper.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/papers/<int:paper_id>', methods=['PUT'])
def update_paper(paper_id):
    """Update paper"""
    session = get_session()
    try:
        paper = session.query(Paper).filter_by(id=paper_id).first()

        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        data = request.get_json()

        # Update fields
        if 'title' in data:
            paper.title = data['title']
        if 'abstract' in data:
            paper.abstract = data['abstract']
        if 'category' in data:
            paper.category = data['category']
        if 'summary' in data:
            paper.summary = data['summary']
        if 'keywords' in data:
            paper.keywords = data['keywords']

        session.commit()

        return jsonify(paper.to_dict()), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/papers/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """Delete paper"""
    session = get_session()
    try:
        paper = session.query(Paper).filter_by(id=paper_id).first()

        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        session.delete(paper)
        session.commit()

        return jsonify({'message': 'Paper deleted'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============================================================================
# Search Routes
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search_papers():
    """Search papers locally"""
    session = get_session()
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')

        papers_query = session.query(Paper)

        if query:
            papers_query = papers_query.filter(
                (Paper.title.ilike(f'%{query}%')) |
                (Paper.abstract.ilike(f'%{query}%')) |
                (Paper.authors.ilike(f'%{query}%'))
            )

        if category:
            papers_query = papers_query.filter(Paper.category == category)

        papers = papers_query.all()

        return jsonify({
            'query': query,
            'count': len(papers),
            'papers': [p.to_dict() for p in papers]
        }), 200
    finally:
        session.close()


@app.route('/api/arxiv/search', methods=['GET'])
def search_arxiv():
    """Search arXiv"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        max_results = request.args.get('max_results', 50, type=int)

        if not query:
            return jsonify({'error': 'Query required'}), 400

        papers = arxiv_service.search(
            query=query,
            category=category if category else None,
            max_results=max_results
        )

        return jsonify({
            'query': query,
            'count': len(papers),
            'papers': papers
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# arXiv Integration Routes
# ============================================================================

@app.route('/api/arxiv/fetch', methods=['POST'])
def arxiv_fetch():
    """Fetch and import paper from arXiv"""
    session = get_session()
    try:
        data = request.get_json()
        arxiv_id = data.get('arxiv_id')

        if not arxiv_id:
            return jsonify({'error': 'arxiv_id required'}), 400

        # Fetch from arXiv
        paper_data = arxiv_service.fetch_paper(arxiv_id)

        if not paper_data:
            return jsonify({'error': 'Paper not found on arXiv'}), 404

        # Check if already exists
        existing = session.query(Paper).filter_by(arxiv_id=arxiv_id).first()
        if existing:
            return jsonify({'message': 'Paper already imported', 'paper': existing.to_dict()}), 200

        # Create paper
        paper = Paper(**paper_data)
        session.add(paper)
        session.commit()

        return jsonify(paper.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/arxiv/parse', methods=['POST'])
def arxiv_parse():
    """Parse arXiv ID from text"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        arxiv_id = arxiv_service.parse_arxiv_id(text)

        if arxiv_id:
            return jsonify({'arxiv_id': arxiv_id}), 200
        else:
            return jsonify({'error': 'No valid arXiv ID found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Tag Routes
# ============================================================================

@app.route('/api/papers/<int:paper_id>/tags', methods=['POST'])
def add_tag(paper_id):
    """Add tag to paper"""
    session = get_session()
    try:
        paper = session.query(Paper).filter_by(id=paper_id).first()
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        data = request.get_json()
        tag_name = data.get('tag_name')

        if not tag_name:
            return jsonify({'error': 'tag_name required'}), 400

        # Check if already exists
        existing = session.query(Tag).filter_by(paper_id=paper_id, tag_name=tag_name).first()
        if existing:
            return jsonify({'message': 'Tag already exists'}), 200

        tag = Tag(paper_id=paper_id, tag_name=tag_name)
        session.add(tag)
        session.commit()

        return jsonify(tag.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============================================================================
# Collection Routes
# ============================================================================

@app.route('/api/collections', methods=['GET'])
def list_collections():
    """List all collections"""
    session = get_session()
    try:
        collections = session.query(Collection).all()
        return jsonify([c.to_dict() for c in collections]), 200
    finally:
        session.close()


@app.route('/api/collections', methods=['POST'])
def create_collection():
    """Create new collection"""
    session = get_session()
    try:
        data = request.get_json()

        collection = Collection(
            name=data.get('name'),
            description=data.get('description')
        )

        session.add(collection)
        session.commit()

        return jsonify(collection.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============================================================================
# Web Routes
# ============================================================================

@app.route('/', methods=['GET'])
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('../web', filename)


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Research Paper Manager starting...")
    print(f"📚 Database: {DB_PATH}")
    print(f"🌐 API: http://localhost:5002/api")
    print(f"📖 Dashboard: http://localhost:5002/dashboard")

    app.run(host='0.0.0.0', port=5002, debug=True)
