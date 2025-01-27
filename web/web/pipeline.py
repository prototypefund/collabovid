PIPELINE = {
    'PIPELINE_ENABLED': False,
    'JS_COMPRESSOR': 'pipeline.compressors.jsmin.JSMinCompressor',
    'CSS_COMPRESSOR': 'pipeline.compressors.cssmin.CSSMinCompressor',
    'JAVASCRIPT': {
        'base': {
            'source_filenames': (
                'js/jquery.min.js',
                'js/popper.min.js',
                'js/bootstrap.min.js',
                'js/jquery.ihavecookies.js',
                'core/js/favorites.js'
            ),
            'output_filename': 'base.js'
        },
        'charts': {
            'source_filenames': (
                'js/moment.js',
                'js/Chart.min.js',
                'core/js/chart_colors.js',
                'core/js/collabovid_charts.js',
            ),
            'output_filename': 'charts.js'
        },
        'dashboard-charts': {
            'source_filenames': (
                'js/moment.js',
                'js/Chart.min.js',
                'core/js/chart_colors.js',
                'dashboard/dashboard_charts.js',
            ),
            'output_filename': 'dashboard_charts.js'
        },
        'search': {
            'source_filenames': (
                'js/bootstrap-select.min.js',
                'js/gijgo.min.js',
                'js/tagify.js',
                'core/js/pagination.js',
                'core/js/collabovid_search.js',
                'core/js/filter_utils.js',
                'core/js/paper_cards.js',
                'search/js/export_confirm.js'
            ),
            'output_filename': 'search.js'
        },
        'task-delete': {
            'source_filenames': (
                'dashboard/tasks/delete.js',
            ),
            'output_filename': 'task-delete.js'
        },
        'map': {
            'source_filenames': (
                'js/jquery-jvectormap-2.0.5.min.js',
                'js/jquery-jvectormap-world-merc.js',
            ),
            'output_filename': 'map.js'
        },
        'embedding-visualization': {
            'source_filenames': (
                'js/three.js',
                'js/OrbitControls.js',
                'js/math.min.js',
                'js/bootstrap-slider.min.js',
                'js/tween.umd.js',
                'js/moment.js',
                'core/js/embedding_visualization.js',
                'core/js/embedding_visualization_view.js',
                'core/js/paper_cards.js',
                'search/js/export_confirm.js'
            ),
            'output_filename': 'embedding_visualization.js'
        },
        'similar_papers': {
            'source_filenames': (
                'core/js/pagination.js',
                'search/js/collabovid_js_paginator.js',
                'search/js/collabovid_similar_search.js',
                'core/js/paper_cards.js',
                'search/js/export_confirm.js'
            ),
            'output_filename': 'similar_search.js'
        }
    },
    'STYLESHEETS': {
        'base': {
            'source_filenames': (
                'css/fontawesome.min.css',
                'css/fa-solid.min.css',
                'css/fa-brands.css',
                'css/roboto.css',
                'core/css/cookie.css',
                'core/css/info-cards.css',
            ),
            'output_filename': 'base.css'
        },
        'custom_base': {
            'source_filenames': (
                'core/css/main.css',
            ),
            'output_filename': 'custom_base.css'
        },
        'charts': {
            'source_filenames': (
                'css/Chart.min.css',
            ),
            'output_filename': 'charts.css'
        },
        'search': {
            'source_filenames': (
                'css/bootstrap-select.css',
                'css/gijgo.min.css',
                'css/tagify.css',
            ),
            'output_filename': 'search.css'
        },
        'dashboard': {
            'source_filenames': (
                'dashboard/tasks/dashboard.css',
            ),
            'output_filename': 'dashboard.css',
        },
        'datatable': {
            'source_filenames': (
                'dashboard/scrape/datatable.css',
            ),
            'output_filename': 'datatable.css',
        },
        'map': {
            'source_filenames': (
                'css/jquery-jvectormap-2.0.5.css',
            ),
            'output_filename': 'map.css',
        },
        'embedding_visualization': {
            'source_filenames': (
                'css/bootstrap-slider.css',
                'core/css/embedding.css',
            ),
            'output_filename': 'embedding_visualization.css',
        },
        'conflict_card': {
            'source_filenames': (
                'dashboard/scrape/conflict_card.css',
            ),
            'output_filename': 'conflict_card.css',
        }
    },
}
