'use strict';

document.addEventListener("DOMContentLoaded", function() {

    /***Pagination Logic***/
    const paginationButtons = document.getElementsByClassName('pagination-button');
    const prev = document.getElementById('previous');
    const next = document.getElementById('next');
    let currentActivePage = 0;

    if(paginationButtons.length > 0) {
        for (let i = 0; i < paginationButtons.length; i++) {
            const individualButton = paginationButtons[i];
            individualButton.addEventListener('click', () => {
                for (let x = 0; x < paginationButtons.length; x++) {
                    paginationButtons[x].classList.remove('active');
                }
                individualButton.classList.add('active');
                currentActivePage = i;
            });
        }
    }

    if(prev && next) {
        prev.addEventListener('click', () => {
            paginationButtons[currentActivePage].classList.remove('active');
            if (currentActivePage === 0) {
                currentActivePage = paginationButtons.length - 1;
            } else {
                currentActivePage--;
            }
            paginationButtons[currentActivePage].classList.add('active');
        });

        next.addEventListener('click', () => {
            paginationButtons[currentActivePage].classList.remove('active');
            if (currentActivePage === paginationButtons.length - 1) {
                currentActivePage = 0;
            } else {
                currentActivePage++;
            }
            paginationButtons[currentActivePage].classList.add('active');
        });
    }

    /*** Submit Data Login Check ***/
    const submitButton = document.getElementById("submitDataBtn");

    if(submitButton) {
        submitButton.addEventListener("click", function(e) {
            e.preventDefault(); // Prevent default form submission
            const isLoggedIn = false; // Simulated login status

            if (!isLoggedIn) {
                const modalEl = document.getElementById("loginRequiredModal");
                if(modalEl) {
                    const loginModal = new bootstrap.Modal(modalEl, {
                        backdrop: 'static', // prevent closing by clicking outside
                        keyboard: false
                    });
                    loginModal.show();
                } else {
                    console.error("Modal element not found!");
                }
            } else {
                const form = document.querySelector("form");
                if(form) {
                    form.submit();
                }
            }
        });
    } else {
        console.error("Submit button not found!");
    }

});

document.addEventListener("DOMContentLoaded", function() {
    // ... your existing pagination and submit logic

    // Add Another Compound Logic
    const addCompoundBtn = document.getElementById("addCompoundBtn");
    const compoundContainer = document.getElementById("compound-entry");

    if(addCompoundBtn && compoundContainer) {
        addCompoundBtn.addEventListener("click", function() {
            // Clone the first compound row
            const firstRow = compoundContainer.querySelector(".compound-row");
            if(firstRow) {
                const newRow = firstRow.cloneNode(true);

                // Clear values in the cloned row
                newRow.querySelectorAll("input").forEach(input => input.value = "");

                // Append to container
                compoundContainer.appendChild(newRow);
            }
        });
    }
});

