document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Single prediction form submission
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.success) {
                    displayResults(data.prediction);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error submitting form: ' + error.message);
            }
        });
    }

    // Batch prediction form submission
    const batchForm = document.getElementById('batchForm');
    if (batchForm) {
        batchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('batchFile');
            formData.append('file', fileInput.files[0]);
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.success) {
                    displayBatchResults(data.download_url);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error processing batch: ' + error.message);
            }
        });
    }
});

function displayResults(prediction) {
    const resultsDiv = document.getElementById('results');
    const predictionSpan = document.getElementById('prediction');
    const confidenceBar = document.getElementById('confidenceBar');
    const probabilitiesDiv = document.getElementById('probabilities');
    
    // Display prediction
    predictionSpan.textContent = prediction.prediction;
    
    // Display confidence
    const confidence = Math.max(...Object.values(prediction.probabilities)) * 100;
    confidenceBar.style.width = `${confidence}%`;
    confidenceBar.setAttribute('aria-valuenow', confidence);
    
    // Display probabilities
    probabilitiesDiv.innerHTML = '<h6>Probabilities:</h6>';
    for (const [disorder, prob] of Object.entries(prediction.probabilities)) {
        const probPercent = (prob * 100).toFixed(1);
        probabilitiesDiv.innerHTML += `
            <div class="mb-2">
                <strong>${disorder}:</strong> ${probPercent}%
            </div>
        `;
    }
    
    resultsDiv.style.display = 'block';
}

function displayBatchResults(downloadUrl) {
    const batchResults = document.getElementById('batchResults');
    const downloadLink = document.getElementById('downloadLink');
    
    downloadLink.href = downloadUrl;
    batchResults.style.display = 'block';
} 