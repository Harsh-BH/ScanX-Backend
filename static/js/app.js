$(document).ready(function() {
    // Handle file upload form submission
    $('#upload-form').on('submit', function(event) {
        event.preventDefault();

        var fileInput = $('#file-input')[0];

        if (fileInput.files.length === 0) {
            alert('Please select a file.');
            return;
        }

        var formData = new FormData();
        formData.append('file', fileInput.files[0]);

        $('#result').html('Processing...');

        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                var resultHtml = '<h2>Prediction: ' + response.prediction + '</h2>';
                resultHtml += '<p>Confidence: ' + response.confidence + '%</p>';
                resultHtml += '<p>Total Faces Analyzed: ' + response.total_faces_analyzed + '</p>';
                resultHtml += '<p>Processing Time: ' + response.processing_time + ' seconds</p>';

                if (response.details && response.details.length > 0) {
                    resultHtml += '<h3>Per-frame Analysis:</h3><ul>';
                    response.details.forEach(function(frameInfo) {
                        resultHtml += '<li>Frame ' + frameInfo.frame_number + ' (Time: ' + frameInfo.timestamp + 's): ' + frameInfo.confidence + '% confidence</li>';
                    });
                    resultHtml += '</ul>';
                }

                $('#result').html(resultHtml);
                plotConfidenceChart(response.details);
            },
            error: function(xhr, status, error) {
                var errorMessage = 'An error occurred: ';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage += xhr.responseJSON.error;
                } else {
                    errorMessage += error;
                }
                $('#result').html('<p style="color:red;">' + errorMessage + '</p>');
            }
        });
    });

    // Handle text prediction button click
    $('#predict-text-button').on('click', function() {
        var textInput = $('#text-input').val();

        if (!textInput) {
            alert('Please enter text to predict.');
            return;
        }

        $('#text-prediction-result').html('Processing...');

        $.ajax({
            url: '/text',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ text: textInput }),
            success: function(response) {
                $('#text-prediction-result').html('<h2>Prediction: ' + response.classification + '</h2>');
            },
            error: function(xhr, status, error) {
                var errorMessage = 'An error occurred: ';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage += xhr.responseJSON.error;
                } else {
                    errorMessage += error;
                }
                $('#text-prediction-result').html('<p style="color:red;">' + errorMessage + '</p>');
            }
        });
    });
});

// Function to plot the confidence chart
function plotConfidenceChart(details) {
    if (!details || details.length === 0) {
        return;
    }

    var labels = details.map(function(frameInfo) {
        return frameInfo.timestamp + 's';
    });
    var data = details.map(function(frameInfo) {
        return frameInfo.confidence;
    });

    // Destroy previous chart instance if it exists
    if (window.confidenceChart) {
        window.confidenceChart.destroy();
    }

    var ctx = document.getElementById('confidenceChart').getContext('2d');
    window.confidenceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Confidence Level (%)',
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
                lineTension: 0
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        max: 100
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Confidence (%)'
                    }
                }],
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Time (s)'
                    }
                }]
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
