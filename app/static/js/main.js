// CarePlus Hospital Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile & Desktop Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show-mobile');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
        if (window.innerWidth <= 992 && sidebar && sidebar.classList.contains('show-mobile')) {
            if (!sidebar.contains(e.target) && sidebarToggleBtn && !sidebarToggleBtn.contains(e.target)) {
                sidebar.classList.remove('show-mobile');
            }
        }
    });

    // 2. Global Live Omnisearch
    const omnisearchInput = document.getElementById('omnisearchInput');
    const omnisearchResults = document.getElementById('omnisearchResults');
    let searchDebounceTimer = null;

    if (omnisearchInput && omnisearchResults) {
        omnisearchInput.addEventListener('input', function () {
            const query = this.value.trim();
            clearTimeout(searchDebounceTimer);

            if (query.length < 2) {
                omnisearchResults.classList.remove('show');
                omnisearchResults.innerHTML = '';
                return;
            }

            searchDebounceTimer = setTimeout(() => {
                fetch(`/api/omnisearch?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            let html = '';
                            data.results.forEach(item => {
                                let badgeColor = 'bg-primary';
                                if (item.category === 'Doctors') badgeColor = 'bg-info text-dark';
                                if (item.category === 'Pharmacy') badgeColor = 'bg-success';
                                if (item.category === 'Billing') badgeColor = 'bg-warning text-dark';

                                html += `
                                    <a href="${item.url}" class="omnisearch-item">
                                        <div class="d-flex align-items-center justify-content-between">
                                            <span class="fw-bold">${item.title}</span>
                                            <span class="badge ${badgeColor}">${item.category}</span>
                                        </div>
                                        <div class="text-muted small">${item.subtitle}</div>
                                    </a>
                                `;
                            });
                            omnisearchResults.innerHTML = html;
                            omnisearchResults.classList.add('show');
                        } else {
                            omnisearchResults.innerHTML = '<div class="p-3 text-muted text-center small">No records found</div>';
                            omnisearchResults.classList.add('show');
                        }
                    })
                    .catch(err => {
                        console.error('Search error:', err);
                    });
            }, 250);
        });

        // Close search results when clicking outside
        document.addEventListener('click', function (e) {
            if (!omnisearchInput.contains(e.target) && !omnisearchResults.contains(e.target)) {
                omnisearchResults.classList.remove('show');
            }
        });
    }

    // 3. Dynamic Cascading Bed Selector
    const roomSelect = document.getElementById('room_id');
    const bedSelect = document.getElementById('bed_id');

    if (roomSelect && bedSelect) {
        roomSelect.addEventListener('change', function () {
            const roomId = this.value;
            if (!roomId || roomId === '0') {
                bedSelect.innerHTML = '<option value="">-- Select Room First --</option>';
                return;
            }

            fetch(`/api/rooms/${roomId}/available-beds`)
                .then(res => res.json())
                .then(beds => {
                    bedSelect.innerHTML = '';
                    if (beds.length === 0) {
                        bedSelect.innerHTML = '<option value="">-- No Available Beds in this Room --</option>';
                    } else {
                        bedSelect.innerHTML = '<option value="">-- Select Available Bed --</option>';
                        beds.forEach(b => {
                            bedSelect.innerHTML += `<option value="${b.id}">${b.bed_number}</option>`;
                        });
                    }
                })
                .catch(err => console.error('Error fetching beds:', err));
        });
    }

    // 4. Dynamic Line Items for Prescription Builder
    const addRxItemBtn = document.getElementById('addRxItemBtn');
    const rxItemsContainer = document.getElementById('rxItemsContainer');

    if (addRxItemBtn && rxItemsContainer) {
        addRxItemBtn.addEventListener('click', function () {
            const rowCount = rxItemsContainer.children.length;
            const newRow = document.createElement('div');
            newRow.className = 'row g-2 rx-item-row mb-2 align-items-end';
            newRow.innerHTML = `
                <div class="col-md-3">
                    <label class="form-label small fw-semibold">Medicine Name</label>
                    <input type="text" name="med_name[]" class="form-control form-control-sm" placeholder="e.g. Paracetamol" required>
                    <input type="hidden" name="med_id[]" value="0">
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Dosage</label>
                    <input type="text" name="dosage[]" class="form-control form-control-sm" placeholder="e.g. 500 mg" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Frequency</label>
                    <input type="text" name="frequency[]" class="form-control form-control-sm" placeholder="e.g. 1-0-1" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Duration</label>
                    <input type="text" name="duration[]" class="form-control form-control-sm" placeholder="e.g. 5 days" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label small fw-semibold">Instructions</label>
                    <input type="text" name="instructions[]" class="form-control form-control-sm" placeholder="e.g. After food" value="After food">
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-sm btn-outline-danger w-100 remove-row-btn"><i class="bi bi-trash"></i></button>
                </div>
            `;
            rxItemsContainer.appendChild(newRow);
            attachRowRemoveHandlers();
        });

        function attachRowRemoveHandlers() {
            document.querySelectorAll('.remove-row-btn').forEach(btn => {
                btn.onclick = function () {
                    const row = this.closest('.rx-item-row');
                    if (rxItemsContainer.children.length > 1) {
                        row.remove();
                    } else {
                        alert('Prescription must contain at least one medication.');
                    }
                };
            });
        }
        attachRowRemoveHandlers();
    }

    // 5. Dynamic Line Items for Invoice Generator
    const addInvoiceItemBtn = document.getElementById('addInvoiceItemBtn');
    const invoiceItemsContainer = document.getElementById('invoiceItemsContainer');

    if (addInvoiceItemBtn && invoiceItemsContainer) {
        addInvoiceItemBtn.addEventListener('click', function () {
            const newRow = document.createElement('tr');
            newRow.className = 'invoice-item-row';
            newRow.innerHTML = `
                <td>
                    <select name="item_type[]" class="form-select form-select-sm">
                        <option value="Consultation">Consultation</option>
                        <option value="Room Charge">Room Charge</option>
                        <option value="Lab Test">Lab Test</option>
                        <option value="Medicine">Medicine</option>
                        <option value="Procedure">Procedure</option>
                        <option value="Nursing">Nursing</option>
                        <option value="General" selected>General</option>
                    </select>
                </td>
                <td>
                    <input type="text" name="item_name[]" class="form-control form-control-sm" placeholder="Item description / service" required>
                </td>
                <td>
                    <input type="number" name="quantity[]" class="form-control form-control-sm item-qty" value="1" min="1" required>
                </td>
                <td>
                    <input type="number" step="0.01" name="unit_price[]" class="form-control form-control-sm item-price" value="0.00" min="0" required>
                </td>
                <td class="text-end fw-bold item-line-total">₹0.00</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger remove-inv-row-btn"><i class="bi bi-trash"></i></button>
                </td>
            `;
            invoiceItemsContainer.appendChild(newRow);
            attachInvoiceRowHandlers();
            calculateInvoiceTotals();
        });

        function attachInvoiceRowHandlers() {
            document.querySelectorAll('.remove-inv-row-btn').forEach(btn => {
                btn.onclick = function () {
                    if (invoiceItemsContainer.querySelectorAll('.invoice-item-row').length > 1) {
                        this.closest('.invoice-item-row').remove();
                        calculateInvoiceTotals();
                    } else {
                        alert('Invoice must have at least one line item.');
                    }
                };
            });

            document.querySelectorAll('.item-qty, .item-price').forEach(input => {
                input.oninput = calculateInvoiceTotals;
            });
        }

        const discountInput = document.getElementById('discount_value');
        const discountTypeSelect = document.getElementById('discount_type');
        const taxRateInput = document.getElementById('tax_rate');

        if (discountInput) discountInput.oninput = calculateInvoiceTotals;
        if (discountTypeSelect) discountTypeSelect.onchange = calculateInvoiceTotals;
        if (taxRateInput) taxRateInput.oninput = calculateInvoiceTotals;

        function calculateInvoiceTotals() {
            let subtotal = 0;
            const rows = invoiceItemsContainer.querySelectorAll('.invoice-item-row');
            rows.forEach(row => {
                const qty = parseFloat(row.querySelector('.item-qty').value) || 0;
                const price = parseFloat(row.querySelector('.item-price').value) || 0;
                const lineTotal = qty * price;
                row.querySelector('.item-line-total').textContent = '₹' + lineTotal.toFixed(2);
                subtotal += lineTotal;
            });

            const subtotalElem = document.getElementById('invSubtotalDisplay');
            if (subtotalElem) subtotalElem.textContent = '₹' + subtotal.toFixed(2);

            let discount = 0;
            const discVal = parseFloat(discountInput ? discountInput.value : 0) || 0;
            const discType = discountTypeSelect ? discountTypeSelect.value : 'Fixed';
            if (discType === 'Percentage') {
                discount = subtotal * (discVal / 100);
            } else {
                discount = Math.min(discVal, subtotal);
            }

            const taxable = Math.max(0, subtotal - discount);
            const taxRate = parseFloat(taxRateInput ? taxRateInput.value : 5) || 0;
            const taxAmount = taxable * (taxRate / 100);
            const grandTotal = taxable + taxAmount;

            const taxElem = document.getElementById('invTaxDisplay');
            const grandTotalElem = document.getElementById('invGrandTotalDisplay');

            if (taxElem) taxElem.textContent = '₹' + taxAmount.toFixed(2);
            if (grandTotalElem) grandTotalElem.textContent = '₹' + grandTotal.toFixed(2);
        }

        attachInvoiceRowHandlers();
    }
});
