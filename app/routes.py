from flask import request, jsonify
from flask import request as flask_request
from .models import db, Bank, Branch
from .schema import schema
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/api/banks', methods=['GET'])
    def get_banks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            banks = Bank.query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'data': [bank.to_dict() for bank in banks.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': banks.total,
                    'pages': banks.pages,
                    'has_next': banks.has_next,
                    'has_prev': banks.has_prev
                }
            })
        except Exception as e:
            logger.error(f"Error in get_banks: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/banks/<int:bank_id>/branches', methods=['GET'])
    def get_bank_branches(bank_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            
            bank = Bank.query.get_or_404(bank_id)
            branches = Branch.query.filter_by(bank_id=bank_id).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'bank': bank.to_dict(),
                'branches': [branch.to_dict() for branch in branches.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': branches.total,
                    'pages': branches.pages,
                    'has_next': branches.has_next,
                    'has_prev': branches.has_prev
                }
            })
        except Exception as e:
            logger.error(f"Error in get_bank_branches: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/branches', methods=['GET'])
    def get_branches():
        try:
            ifsc = request.args.get('ifsc')
            city = request.args.get('city')
            state = request.args.get('state')
            district = request.args.get('district')
            bank_name = request.args.get('bank_name')
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            
            query = Branch.query
            
            if ifsc:
                query = query.filter(Branch.ifsc.ilike(f'%{ifsc}%'))
            if city:
                query = query.filter(Branch.city.ilike(f'%{city}%'))
            if state:
                query = query.filter(Branch.state.ilike(f'%{state}%'))
            if district:
                query = query.filter(Branch.district.ilike(f'%{district}%'))
            if bank_name:
                query = query.join(Bank).filter(Bank.name.ilike(f'%{bank_name}%'))
            
            branches = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'data': [branch.to_dict() for branch in branches.items],
                'filters': {
                    'ifsc': ifsc,
                    'city': city,
                    'state': state,
                    'district': district,
                    'bank_name': bank_name
                },
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': branches.total,
                    'pages': branches.pages,
                    'has_next': branches.has_next,
                    'has_prev': branches.has_prev
                }
            })
        except Exception as e:
            logger.error(f"Error in get_branches: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/branches/<ifsc>', methods=['GET'])
    def get_branch_by_ifsc(ifsc):
        try:
            branch = Branch.query.filter_by(ifsc=ifsc.upper()).first_or_404()
            return jsonify({
                'success': True,
                'data': branch.to_dict()
            })
        except Exception as e:
            logger.error(f"Error in get_branch_by_ifsc: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/search', methods=['GET'])
    def search_branches():
        try:
            search_term = request.args.get('q', '').strip()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            if not search_term:
                return jsonify({
                    'success': False,
                    'error': 'Search term (q) is required'
                }), 400
            
            query = Branch.query.join(Bank).filter(
                db.or_(
                    Branch.ifsc.ilike(f'%{search_term}%'),
                    Branch.branch.ilike(f'%{search_term}%'),
                    Branch.city.ilike(f'%{search_term}%'),
                    Branch.district.ilike(f'%{search_term}%'),
                    Branch.state.ilike(f'%{search_term}%'),
                    Branch.address.ilike(f'%{search_term}%'),
                    Bank.name.ilike(f'%{search_term}%')
                )
            )
            
            branches = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'search_term': search_term,
                'data': [branch.to_dict() for branch in branches.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': branches.total,
                    'pages': branches.pages,
                    'has_next': branches.has_next,
                    'has_prev': branches.has_prev
                }
            })
        except Exception as e:
            logger.error(f"Error in search_branches: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        try:
            total_banks = Bank.query.count()
            total_branches = Branch.query.count()
            
            top_banks = db.session.query(
                Bank.name,
                db.func.count(Branch.id).label('branch_count')
            ).join(Branch).group_by(Bank.id, Bank.name).order_by(
                db.func.count(Branch.id).desc()
            ).limit(10).all()
            
            branches_by_state = db.session.query(
                Branch.state,
                db.func.count(Branch.id).label('branch_count')
            ).group_by(Branch.state).order_by(
                db.func.count(Branch.id).desc()
            ).limit(10).all()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_banks': total_banks,
                    'total_branches': total_branches,
                    'top_banks_by_branches': [
                        {'bank_name': bank[0], 'branch_count': bank[1]} 
                        for bank in top_banks
                    ],
                    'top_states_by_branches': [
                        {'state': state[0], 'branch_count': state[1]} 
                        for state in branches_by_state
                    ]
                }
            })
        except Exception as e:
            logger.error(f"Error in get_stats: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/gql', methods=['GET', 'POST'])
    def graphql_server():
        if flask_request.method == 'GET':
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Indian Banks GraphiQL</title>
                <link rel="stylesheet" href="https://unpkg.com/graphiql/graphiql.min.css" />
                <style>
                    body { margin: 0; font-family: Arial, sans-serif; }
                    .header { background: #2c3e50; color: white; padding: 10px 20px; }
                    .header h1 { margin: 0; font-size: 1.5em; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🏦 Indian Banks GraphQL API</h1>
                    <p>Query over 127,000+ bank branches across India</p>
                </div>
                <div id="graphiql" style="height: calc(100vh - 80px);"></div>
                <script crossorigin src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
                <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
                <script crossorigin src="https://unpkg.com/graphiql/graphiql.min.js"></script>
                <script>
                    ReactDOM.render(
                        React.createElement(GraphiQL, {
                            fetcher: function(params) {
                                return fetch('/gql', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify(params),
                                })
                                .then(response => response.json());
                            },
                            defaultQuery: `# Welcome to Indian Banks GraphQL API
# Query examples:

# Get all banks
query GetBanks {
  banks {
    edges {
      node {
        id
        name
      }
    }
  }
}

# Search for a specific branch by IFSC
query GetBranchByIFSC {
  branchByIfsc(ifsc: "SBIN0000001") {
    ifsc
    branch
    city
    state
    bank {
      name
    }
  }
}

# Get branches by bank name
query GetSBIBranches {
  branchesByBank(bankName: "State Bank") {
    ifsc
    branch
    city
    state
  }
}`
                        }),
                        document.getElementById('graphiql')
                    );
                </script>
            </body>
            </html>
            '''
        else:
            try:
                data = flask_request.get_json()
                query = data.get('query')
                variables = data.get('variables')
                
                result = schema.execute(query, variables=variables)
                
                response_data = {'data': result.data}
                if result.errors:
                    response_data['errors'] = [str(error) for error in result.errors]
                
                return jsonify(response_data)
            except Exception as e:
                logger.error(f"Error in GraphQL endpoint: {str(e)}")
                return jsonify({'errors': [str(e)]}), 400

    @app.route('/')
    def index():
        return jsonify({
            'message': '🏦 Indian Banks API Server',
            'description': 'Complete API for Indian bank branches with IFSC codes',
            'data_source': 'Based on RBI data via https://github.com/snarayanank2/indian_banks',
            'total_records': {
                'banks': Bank.query.count() if Bank.query.first() else 0,
                'branches': Branch.query.count() if Branch.query.first() else 0
            },
            'endpoints': {
                'REST API': {
                    'GET /api/banks': 'Get all banks (with pagination)',
                    'GET /api/banks/<bank_id>/branches': 'Get branches for specific bank',
                    'GET /api/branches': 'Get all branches (supports filtering & pagination)',
                    'GET /api/branches/<ifsc>': 'Get specific branch by IFSC',
                    'GET /api/search?q=<term>': 'Search across all fields',
                    'GET /api/stats': 'Get database statistics'
                },
                'GraphQL': {
                    'POST /gql': 'GraphQL endpoint',
                    'GET /gql': 'GraphiQL interface for testing'
                }
            },
            'sample_queries': {
                'REST': {
                    'All banks': '/api/banks',
                    'Banks with pagination': '/api/banks?page=1&per_page=10',
                    'Filter by city': '/api/branches?city=Mumbai&page=1',
                    'Filter by state': '/api/branches?state=Maharashtra',
                    'Filter by bank name': '/api/branches?bank_name=State%20Bank',
                    'Search everything': '/api/search?q=Mumbai',
                    'Specific IFSC': '/api/branches/SBIN0000001',
                    'Statistics': '/api/stats'
                },
                'GraphQL': {
                    'Banks': '{ banks { edges { node { name } } } }',
                    'Branch by IFSC': '{ branchByIfsc(ifsc: "SBIN0000001") { branch city bank { name } } }',
                    'Branches by bank': '{ branchesByBank(bankName: "HDFC") { ifsc branch city } }',
                    'Branches by city': '{ branchesByCity(city: "Mumbai") { ifsc branch bank { name } } }'
                }
            }
        })
