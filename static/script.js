const btn = document.getElementById('backToTop');
const container = document.querySelector('.container');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            btn.classList.add('show');
        } else {
            btn.classList.remove('show');
        }
    });
}, { threshold: 0 });

if (container) {
    observer.observe(container);
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

const form = document.getElementById('prediction-form');
const resultContainer = document.getElementById('result-container');
const priceRangeText = document.getElementById('price-range');

if (form) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault(); 
        
        const requestData = {
            overall_qual: parseInt(document.getElementById('overall_qual').value),
            gr_liv_area: parseFloat(document.getElementById('gr_liv_area').value),
            total_bsmt_sf: parseFloat(document.getElementById('total_bsmt_sf').value),
            tot_rms_abv_grd: parseInt(document.getElementById('tot_rms_abv_grd').value),
            full_bath: parseInt(document.getElementById('full_bath').value),
            garage_cars: parseInt(document.getElementById('garage_cars').value),
            age: parseInt(document.getElementById('age').value),
            neighborhood: document.getElementById('neighborhood').value,
            foundation: document.getElementById('foundation').value,
            building_type: document.getElementById('building_type').value,
            sale_type: document.getElementById('sale_type').value,
            sale_condition: document.getElementById('sale_condition').value
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error("FastAPI Error Details:", errorData);
                throw new Error("Data mismatch - check console");
            }

            const result = await response.json();
            priceRangeText.innerText = `$${result.lower_bound.toLocaleString()} — $${result.upper_bound.toLocaleString()}`;
            resultContainer.style.display = 'block';
        } catch (error) {
            priceRangeText.innerText = "Error calculating price. Check Console.";
            resultContainer.style.display = 'block';
        }
    });
}

async function loadAnalysisGraph() {
    try {
        const response = await fetch('/api/analysis-graph');
        const graphData = await response.json();
        Plotly.newPlot('scatter-plot', graphData.data, graphData.layout, {responsive: true});
    } catch (error) {}
}

async function loadboxPlot() {
    try {
        const response = await fetch('/api/boxplot-graph'); 
        const boxPlotData = await response.json();
        Plotly.newPlot('boxplot', boxPlotData.data, boxPlotData.layout, {responsive: true});
    } catch (error) {}
}

async function loadLinePlot() {
    try {
        const response = await fetch('/api/lineplot'); 
        const LinePlot = await response.json();
        Plotly.newPlot('lineplot', LinePlot.data, LinePlot.layout, {responsive: true});
    } catch (error) {
        console.error(error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAnalysisGraph();
    loadboxPlot();
    loadLinePlot();
});