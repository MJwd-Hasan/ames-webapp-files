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
    }, { 
        threshold: 0 
    });

observer.observe(container);

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

const form = document.getElementById('prediction-form');
const resultContainer = document.getElementById('result-container');
const priceRangeText = document.getElementById('price-range');

form.addEventListener('submit', async function(event) {
    event.preventDefault(); 

    // Gather data (Only the 3 inputs that exist in your HTML)
    const requestData = {
        overall_qual: parseInt(document.getElementById('overall_qual').value),
        gr_liv_area: parseInt(document.getElementById('gr_liv_area').value),
        total_bsmt_sf: parseFloat(document.getElementById('total_bsmt_sf').value)
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        priceRangeText.innerText = `$${result.lower_bound.toLocaleString()} — $${result.upper_bound.toLocaleString()}`;
        resultContainer.style.display = 'block';

    } catch (error) {
        console.error("Error:", error);
        priceRangeText.innerText = "Error calculating price.";
        resultContainer.style.display = 'block';
    }
});