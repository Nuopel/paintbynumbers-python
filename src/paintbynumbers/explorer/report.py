"""HTML report generator for exploration results."""

from pathlib import Path
from typing import List
import json
from datetime import datetime

from .engine import VariationResult


class HTMLReportGenerator:
    """Generates interactive HTML reports for exploration results."""

    def __init__(self, results: List[VariationResult], output_dir: Path):
        """Initialize report generator.

        Args:
            results: List of variation results
            output_dir: Directory containing exploration results
        """
        self.results = results
        self.output_dir = Path(output_dir)
        self.successful_results = [r for r in results if r.success]

    def generate(self, output_path: Path) -> None:
        """Generate HTML report.

        Args:
            output_path: Path to save HTML file
        """
        html = self._generate_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"HTML report saved to: {output_path}")

    def _generate_html(self) -> str:
        """Generate complete HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paint-by-Numbers Explorer Results</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        {self._get_header()}
        {self._get_controls()}
        {self._get_comparison_section()}
        {self._get_grid()}
    </div>
    {self._get_scripts()}
</body>
</html>"""

    def _get_styles(self) -> str:
        """Generate CSS styles."""
        return """<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
            color: #2c3e50;
        }

        .header .stats {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .stat {
            display: flex;
            flex-direction: column;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }

        .controls {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .controls h2 {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #2c3e50;
        }

        .filter-section {
            margin-bottom: 20px;
        }

        .filter-label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
        }

        .filter-inputs {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }

        .filter-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="number"], select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 0.95em;
        }

        input[type="number"] {
            width: 100px;
        }

        select {
            min-width: 150px;
        }

        .sort-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }

        button {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: background 0.2s;
        }

        button:hover {
            background: #2980b9;
        }

        button.secondary {
            background: #95a5a6;
        }

        button.secondary:hover {
            background: #7f8c8d;
        }

        .comparison-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: none;
        }

        .comparison-section.active {
            display: block;
        }

        .comparison-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .comparison-item {
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 15px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }

        .card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }

        .card.selected {
            outline: 3px solid #3498db;
            outline-offset: 2px;
        }

        .card.error {
            opacity: 0.6;
            background: #fee;
        }

        .card-image {
            width: 100%;
            height: 300px;
            object-fit: contain;
            background: #f9f9f9;
            border-bottom: 1px solid #eee;
        }

        .card-content {
            padding: 20px;
        }

        .card-title {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .card-params {
            margin-bottom: 15px;
            font-size: 0.9em;
        }

        .param-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dotted #eee;
        }

        .param-label {
            color: #666;
        }

        .param-value {
            font-weight: 600;
            color: #333;
        }

        .card-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            padding-top: 15px;
            border-top: 2px solid #eee;
            font-size: 0.85em;
        }

        .metric {
            display: flex;
            flex-direction: column;
        }

        .metric-label {
            color: #666;
            font-size: 0.9em;
        }

        .metric-value {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }

        .error-message {
            color: #e74c3c;
            background: #fee;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
        }

        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #999;
            font-size: 1.2em;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            overflow: auto;
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 90%;
            max-height: 90%;
            overflow: auto;
        }

        .modal-close {
            float: right;
            font-size: 2em;
            cursor: pointer;
            color: #999;
        }

        .modal-close:hover {
            color: #333;
        }

        .modal-image {
            width: 100%;
            max-width: 1200px;
            height: auto;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .filter-inputs, .sort-controls {
                flex-direction: column;
                align-items: stretch;
            }

            .filter-group {
                flex-direction: column;
                align-items: stretch;
            }

            input[type="number"], select {
                width: 100%;
            }
        }
    </style>"""

    def _get_header(self) -> str:
        """Generate header section."""
        total = len(self.results)
        successful = len(self.successful_results)
        failed = total - successful

        # Calculate average metrics
        if self.successful_results:
            avg_time = sum(r.metrics.processing_time for r in self.successful_results) / len(self.successful_results)
            avg_facets = sum(r.metrics.num_facets for r in self.successful_results) / len(self.successful_results)
        else:
            avg_time = 0
            avg_facets = 0

        return f"""<div class="header">
        <h1>Paint-by-Numbers Explorer Results</h1>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}</p>
        <div class="stats">
            <div class="stat">
                <span class="stat-label">Total Variations</span>
                <span class="stat-value">{total}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Successful</span>
                <span class="stat-value" style="color: #27ae60;">{successful}</span>
            </div>
            {f'<div class="stat"><span class="stat-label">Failed</span><span class="stat-value" style="color: #e74c3c;">{failed}</span></div>' if failed > 0 else ''}
            <div class="stat">
                <span class="stat-label">Avg Processing Time</span>
                <span class="stat-value">{avg_time:.2f}s</span>
            </div>
            <div class="stat">
                <span class="stat-label">Avg Facets</span>
                <span class="stat-value">{avg_facets:.0f}</span>
            </div>
        </div>
    </div>"""

    def _get_controls(self) -> str:
        """Generate filter and sort controls."""
        return """<div class="controls">
        <h2>Filter & Sort</h2>

        <div class="filter-section">
            <label class="filter-label">Filter by Metrics</label>
            <div class="filter-inputs">
                <div class="filter-group">
                    <span>Facets:</span>
                    <input type="number" id="facets-min" placeholder="Min">
                    <input type="number" id="facets-max" placeholder="Max">
                </div>
                <div class="filter-group">
                    <span>Colors:</span>
                    <input type="number" id="colors-min" placeholder="Min">
                    <input type="number" id="colors-max" placeholder="Max">
                </div>
                <div class="filter-group">
                    <span>Processing Time (s):</span>
                    <input type="number" id="time-min" placeholder="Min" step="0.1">
                    <input type="number" id="time-max" placeholder="Max" step="0.1">
                </div>
            </div>
        </div>

        <div class="filter-section">
            <label class="filter-label">Sort By</label>
            <div class="sort-controls">
                <select id="sort-by">
                    <option value="index">Variation Index</option>
                    <option value="facets">Number of Facets</option>
                    <option value="colors">Number of Colors</option>
                    <option value="time">Processing Time</option>
                    <option value="diversity">Color Diversity</option>
                    <option value="complexity">Border Complexity</option>
                </select>
                <select id="sort-order">
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                </select>
                <button onclick="applyFiltersAndSort()">Apply</button>
                <button class="secondary" onclick="resetFilters()">Reset</button>
            </div>
        </div>

        <div class="filter-section">
            <label class="filter-label">Comparison Mode</label>
            <div class="sort-controls">
                <button id="toggle-comparison" onclick="toggleComparisonMode()">
                    Enable Comparison (select up to 4)
                </button>
                <button class="secondary" onclick="clearComparison()">Clear Selection</button>
            </div>
        </div>
    </div>"""

    def _get_comparison_section(self) -> str:
        """Generate comparison section."""
        return """<div class="comparison-section" id="comparison-section">
        <h2>Comparison View</h2>
        <div id="comparison-grid" class="comparison-grid">
            <!-- Comparison items will be added dynamically -->
        </div>
    </div>"""

    def _get_grid(self) -> str:
        """Generate results grid."""
        cards = [self._get_card(result) for result in self.results]
        cards_html = "\n".join(cards)

        return f"""<div class="grid" id="results-grid">
        {cards_html if cards else '<div class="no-results">No results to display</div>'}
    </div>

    <!-- Modal for full-size image -->
    <div id="image-modal" class="modal" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <img id="modal-image" class="modal-image" src="" alt="Full size">
        </div>
    </div>"""

    def _get_card(self, result: VariationResult) -> str:
        """Generate HTML for a single result card."""
        # Prepare image path (relative to HTML file)
        if result.success and 'png' in result.output_paths:
            # Make path relative to output directory
            rel_path = result.output_paths['png'].relative_to(self.output_dir)
            img_src = str(rel_path).replace('\\', '/')
        else:
            img_src = ""

        # Get parameters that differ from baseline
        param_items = []
        for key, value in sorted(result.parameters.items()):
            # Shorten key for display
            display_key = self._shorten_key(key)
            param_items.append(f"""
                <div class="param-item">
                    <span class="param-label">{display_key}:</span>
                    <span class="param-value">{value}</span>
                </div>
            """)

        params_html = "".join(param_items)

        # Generate metrics section
        if result.success and result.metrics:
            m = result.metrics
            metrics_html = f"""
                <div class="card-metrics">
                    <div class="metric">
                        <span class="metric-label">Facets</span>
                        <span class="metric-value">{m.num_facets}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Colors</span>
                        <span class="metric-value">{m.num_colors}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Time</span>
                        <span class="metric-value">{m.processing_time:.2f}s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Diversity</span>
                        <span class="metric-value">{m.color_diversity_score:.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Avg Facet</span>
                        <span class="metric-value">{m.mean_facet_size:.0f}px</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Complexity</span>
                        <span class="metric-value">{m.avg_border_complexity:.1f}</span>
                    </div>
                </div>
            """
        else:
            metrics_html = f'<div class="error-message">Error: {result.error[:200]}</div>'

        # Generate data attributes for filtering/sorting
        data_attrs = ""
        if result.success and result.metrics:
            m = result.metrics
            data_attrs = f"""
                data-facets="{m.num_facets}"
                data-colors="{m.num_colors}"
                data-time="{m.processing_time:.2f}"
                data-diversity="{m.color_diversity_score:.2f}"
                data-complexity="{m.avg_border_complexity:.1f}"
                data-index="{result.variation_index}"
            """

        error_class = "" if result.success else " error"

        return f"""<div class="card{error_class}"
                       id="card-{result.variation_index}"
                       {data_attrs}
                       onclick="selectCard(this, event)">
        {f'<img class="card-image" src="{img_src}" alt="{result.variation_id}" onclick="openModal(event, this.src)">' if img_src else '<div class="card-image" style="display: flex; align-items: center; justify-content: center; color: #999;">No preview</div>'}
        <div class="card-content">
            <div class="card-title">{result.variation_id}</div>
            <div class="card-params">
                {params_html}
            </div>
            {metrics_html}
        </div>
    </div>"""

    def _shorten_key(self, key: str) -> str:
        """Shorten parameter names for display."""
        replacements = {
            "kMeansNrOfClusters": "Clusters",
            "kMeansClusteringColorSpace": "Color Space",
            "kMeansMinDeltaDifference": "Delta",
            "removeFacetsSmallerThanNrOfPoints": "Min Facet Size",
            "maximumNumberOfFacets": "Max Facets",
            "narrowPixelStripCleanupRuns": "Cleanup Runs",
            "nrOfTimesToHalveBorderSegments": "Border Smoothing",
            "resizeImageWidth": "Width",
            "resizeImageHeight": "Height",
            "removeFacetsFromLargeToSmall": "Remove Large First",
        }
        return replacements.get(key, key)

    def _get_scripts(self) -> str:
        """Generate JavaScript for interactivity."""
        # Convert results to JSON for use in JavaScript
        results_data = []
        for r in self.results:
            if r.success and r.metrics:
                results_data.append({
                    'index': r.variation_index,
                    'id': r.variation_id,
                    'facets': r.metrics.num_facets,
                    'colors': r.metrics.num_colors,
                    'time': r.metrics.processing_time,
                    'diversity': r.metrics.color_diversity_score,
                    'complexity': r.metrics.avg_border_complexity,
                })

        results_json = json.dumps(results_data)

        return f"""<script>
        let comparisonMode = false;
        let selectedCards = new Set();
        const resultsData = {results_json};

        function applyFiltersAndSort() {{
            const facetsMin = parseFloat(document.getElementById('facets-min').value) || -Infinity;
            const facetsMax = parseFloat(document.getElementById('facets-max').value) || Infinity;
            const colorsMin = parseFloat(document.getElementById('colors-min').value) || -Infinity;
            const colorsMax = parseFloat(document.getElementById('colors-max').value) || Infinity;
            const timeMin = parseFloat(document.getElementById('time-min').value) || -Infinity;
            const timeMax = parseFloat(document.getElementById('time-max').value) || Infinity;

            const sortBy = document.getElementById('sort-by').value;
            const sortOrder = document.getElementById('sort-order').value;

            const grid = document.getElementById('results-grid');
            const cards = Array.from(grid.querySelectorAll('.card'));

            // Filter cards
            cards.forEach(card => {{
                const facets = parseFloat(card.dataset.facets) || 0;
                const colors = parseFloat(card.dataset.colors) || 0;
                const time = parseFloat(card.dataset.time) || 0;

                const visible = facets >= facetsMin && facets <= facetsMax &&
                               colors >= colorsMin && colors <= colorsMax &&
                               time >= timeMin && time <= timeMax;

                card.style.display = visible ? 'block' : 'none';
            }});

            // Sort visible cards
            const visibleCards = cards.filter(card => card.style.display !== 'none');

            visibleCards.sort((a, b) => {{
                let aVal, bVal;

                switch(sortBy) {{
                    case 'index':
                        aVal = parseFloat(a.dataset.index) || 0;
                        bVal = parseFloat(b.dataset.index) || 0;
                        break;
                    case 'facets':
                        aVal = parseFloat(a.dataset.facets) || 0;
                        bVal = parseFloat(b.dataset.facets) || 0;
                        break;
                    case 'colors':
                        aVal = parseFloat(a.dataset.colors) || 0;
                        bVal = parseFloat(b.dataset.colors) || 0;
                        break;
                    case 'time':
                        aVal = parseFloat(a.dataset.time) || 0;
                        bVal = parseFloat(b.dataset.time) || 0;
                        break;
                    case 'diversity':
                        aVal = parseFloat(a.dataset.diversity) || 0;
                        bVal = parseFloat(b.dataset.diversity) || 0;
                        break;
                    case 'complexity':
                        aVal = parseFloat(a.dataset.complexity) || 0;
                        bVal = parseFloat(b.dataset.complexity) || 0;
                        break;
                    default:
                        aVal = 0;
                        bVal = 0;
                }}

                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            }});

            // Clear grid and re-add sorted cards
            grid.innerHTML = '';
            visibleCards.forEach(card => grid.appendChild(card));

            // Add back hidden cards at the end
            cards.filter(card => card.style.display === 'none')
                 .forEach(card => grid.appendChild(card));
        }}

        function resetFilters() {{
            document.getElementById('facets-min').value = '';
            document.getElementById('facets-max').value = '';
            document.getElementById('colors-min').value = '';
            document.getElementById('colors-max').value = '';
            document.getElementById('time-min').value = '';
            document.getElementById('time-max').value = '';
            document.getElementById('sort-by').value = 'index';
            document.getElementById('sort-order').value = 'asc';

            applyFiltersAndSort();
        }}

        function toggleComparisonMode() {{
            comparisonMode = !comparisonMode;
            const button = document.getElementById('toggle-comparison');
            button.textContent = comparisonMode ?
                'Disable Comparison' :
                'Enable Comparison (select up to 4)';
            button.style.background = comparisonMode ? '#e74c3c' : '#3498db';

            if (!comparisonMode) {{
                clearComparison();
            }}
        }}

        function selectCard(card, event) {{
            // Don't select if clicking on image (that opens modal)
            if (event.target.tagName === 'IMG') {{
                return;
            }}

            if (!comparisonMode) return;

            const cardId = card.id;

            if (selectedCards.has(cardId)) {{
                selectedCards.delete(cardId);
                card.classList.remove('selected');
            }} else {{
                if (selectedCards.size >= 4) {{
                    alert('Maximum 4 variations can be compared');
                    return;
                }}
                selectedCards.add(cardId);
                card.classList.add('selected');
            }}

            updateComparison();
        }}

        function clearComparison() {{
            selectedCards.clear();
            document.querySelectorAll('.card').forEach(card => {{
                card.classList.remove('selected');
            }});
            updateComparison();
        }}

        function updateComparison() {{
            const section = document.getElementById('comparison-section');
            const grid = document.getElementById('comparison-grid');

            if (selectedCards.size === 0) {{
                section.classList.remove('active');
                return;
            }}

            section.classList.add('active');
            grid.innerHTML = '';

            selectedCards.forEach(cardId => {{
                const originalCard = document.getElementById(cardId);
                const clone = originalCard.cloneNode(true);
                clone.classList.add('comparison-item');
                clone.onclick = null;
                grid.appendChild(clone);
            }});
        }}

        function openModal(event, src) {{
            event.stopPropagation();
            const modal = document.getElementById('image-modal');
            const modalImg = document.getElementById('modal-image');
            modalImg.src = src;
            modal.classList.add('active');
        }}

        function closeModal() {{
            const modal = document.getElementById('image-modal');
            modal.classList.remove('active');
        }}

        // Keyboard shortcut: Escape to close modal
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                closeModal();
                if (comparisonMode) {{
                    toggleComparisonMode();
                }}
            }}
        }});
    </script>"""
