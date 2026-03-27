'use strict';

document.addEventListener("DOMContentLoaded", function () {

    // Pagination Logic 
    const paginationButtons = document.getElementsByClassName('pagination-button');
    const prev = document.getElementById('previous');
    const next = document.getElementById('next');
    let currentActivePage = 0;

    if (paginationButtons.length > 0) {
        for (let i = 0; i < paginationButtons.length; i++) {
            paginationButtons[i].addEventListener('click', () => {
                for (let x = 0; x < paginationButtons.length; x++) {
                    paginationButtons[x].classList.remove('active');
                }
                paginationButtons[i].classList.add('active');
                currentActivePage = i;
            });
        }
    }

    if (prev && next) {
        prev.addEventListener('click', () => {
            paginationButtons[currentActivePage].classList.remove('active');
            currentActivePage = currentActivePage === 0
                ? paginationButtons.length - 1
                : currentActivePage - 1;
            paginationButtons[currentActivePage].classList.add('active');
        });

        next.addEventListener('click', () => {
            paginationButtons[currentActivePage].classList.remove('active');
            currentActivePage = currentActivePage === paginationButtons.length - 1
                ? 0
                : currentActivePage + 1;
            paginationButtons[currentActivePage].classList.add('active');
        });
    }

    // Submit Data Login Check
    const submitButton = document.getElementById("submitDataBtn");
    if (submitButton) {
        submitButton.addEventListener("click", function (e) {
            if (!isLoggedIn) {
                e.preventDefault();
                const modalEl = document.getElementById("loginRequiredModal");
                if (modalEl) {
                    const loginModal = new bootstrap.Modal(modalEl, {
                        backdrop: 'static',
                        keyboard: false
                    });
                    loginModal.show();
                }
            }
        });
    }

    // Add/Remove Compound Entries
    const addCompoundBtn = document.getElementById("addCompoundBtn");
    const compoundContainer = document.getElementById("compound-entry");

    if (addCompoundBtn && compoundContainer) {
        addCompoundBtn.addEventListener("click", function () {
            const firstRow = compoundContainer.querySelector(".compound-row");
            if (firstRow) {
                const newRow = firstRow.cloneNode(true);

                // Clear inputs and remove duplicate IDs
                newRow.querySelectorAll("input").forEach(input => {
                    input.value = "";
                    if (input.id) input.removeAttribute("id");
                });

                // Append remove button if not present
                if (!newRow.querySelector(".remove-compound-btn")) {
                    const removeBtnCol = document.createElement("div");
                    removeBtnCol.className = "col-md-4 d-flex align-items-end";
                    removeBtnCol.innerHTML = '<button type="button" class="btn btn-outline-danger remove-compound-btn">Remove</button>';
                    newRow.appendChild(removeBtnCol);
                }

                compoundContainer.appendChild(newRow);
            }
        });

        // Remove compound row
        compoundContainer.addEventListener("click", function (e) {
            if (e.target && e.target.classList.contains("remove-compound-btn")) {
                const row = e.target.closest(".compound-row");
                if (row && compoundContainer.children.length > 1) {
                    row.remove();
                }
            }
        });
    }

});
