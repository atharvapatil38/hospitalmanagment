// CarePlus HMS - Chart.js Visualizations

document.addEventListener('DOMContentLoaded', function () {
    const revenueChartCanvas = document.getElementById('revenueChart');
    const patientTrendCanvas = document.getElementById('patientTrendChart');
    const deptChartCanvas = document.getElementById('departmentChart');
    const bedChartCanvas = document.getElementById('bedOccupancyChart');
    const aptChartCanvas = document.getElementById('appointmentStatusChart');

    if (!revenueChartCanvas && !patientTrendCanvas) return;

    fetch('/api/dashboard-charts')
        .then(res => res.json())
        .then(data => {
            // 1. Revenue Chart (Area Line)
            if (revenueChartCanvas && data.revenue) {
                new Chart(revenueChartCanvas, {
                    type: 'line',
                    data: {
                        labels: data.revenue.labels,
                        datasets: [{
                            label: 'Monthly Revenue (₹)',
                            data: data.revenue.data,
                            borderColor: '#2563eb',
                            backgroundColor: 'rgba(37, 99, 235, 0.1)',
                            borderWidth: 2.5,
                            tension: 0.35,
                            fill: true,
                            pointBackgroundColor: '#2563eb',
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function (ctx) {
                                        return '₹' + ctx.parsed.y.toLocaleString();
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#f1f5f9' },
                                ticks: {
                                    callback: function (val) {
                                        return '₹' + val.toLocaleString();
                                    }
                                }
                            },
                            x: {
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // 2. Patient Trend Chart (Bar)
            if (patientTrendCanvas && data.patient_trend) {
                new Chart(patientTrendCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.patient_trend.labels,
                        datasets: [{
                            label: 'New Patients',
                            data: data.patient_trend.data,
                            backgroundColor: '#0ea5e9',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { stepSize: 1 } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            // 3. Department Share Chart (Doughnut)
            if (deptChartCanvas && data.departments) {
                new Chart(deptChartCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.departments.labels,
                        datasets: [{
                            data: data.departments.data,
                            backgroundColor: [
                                '#3b82f6', '#10b981', '#f59e0b', '#ec4899',
                                '#8b5cf6', '#06b6d4', '#f97316', '#64748b'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                        },
                        cutout: '65%'
                    }
                });
            }

            // 4. Bed Occupancy (Pie / Doughnut)
            if (bedChartCanvas && data.beds) {
                new Chart(bedChartCanvas, {
                    type: 'pie',
                    data: {
                        labels: data.beds.labels,
                        datasets: [{
                            data: data.beds.data,
                            backgroundColor: ['#ef4444', '#10b981', '#64748b', '#f59e0b']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                        }
                    }
                });
            }

            // 5. Appointment Status Distribution
            if (aptChartCanvas && data.appointments) {
                new Chart(aptChartCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.appointments.labels,
                        datasets: [{
                            data: data.appointments.data,
                            backgroundColor: ['#f59e0b', '#0ea5e9', '#10b981', '#ef4444']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                        },
                        cutout: '60%'
                    }
                });
            }
        })
        .catch(err => console.error('Failed to load dashboard chart metrics:', err));
});
