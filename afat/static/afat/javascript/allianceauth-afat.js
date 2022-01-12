/**
 * Convert a string to a slug
 * @param {string} text
 * @returns {string}
 */
let convertStringToSlug = function (text) {
    'use strict';

    return text.toLowerCase()
        .replace(/[^\w ]+/g, '')
        .replace(/ +/g, '-');
};

/**
 * Sorting a table by its first columns alphabetically
 * @param {element} table
 * @param {string} order
 */
const sortTable = function (table, order) {
    'use strict';

    const asc = order === 'asc';
    const tbody = table.find('tbody');

    tbody.find('tr').sort(function (a, b) {
        if (asc) {
            return $('td:first', a).text().localeCompare($('td:first', b).text());
        } else {
            return $('td:first', b).text().localeCompare($('td:first', a).text());
        }
    }).appendTo(tbody);
};

/**
 * Manage a modal window
 * @param {element} modalElement
 */
const manageModal = function (modalElement) {
    'use strict';

    modalElement.on('show.bs.modal', function (event) {
        const modal = $(this);
        const button = $(event.relatedTarget); // Button that triggered the modal
        const url = button.data('url'); // Extract info from data-* attributes
        const cancelText = button.data('cancel-text');
        const confirmText = button.data('confirm-text');
        const bodyText = button.data('body-text');
        let cancelButtonText = modal.find('#cancelButtonDefaultText').text();
        let confirmButtonText = modal.find('#confirmButtonDefaultText').text();

        if (typeof cancelText !== 'undefined' && cancelText !== '') {
            cancelButtonText = cancelText;
        }

        if (typeof confirmText !== 'undefined' && confirmText !== '') {
            confirmButtonText = confirmText;
        }

        modal.find('#cancel-action').text(cancelButtonText);
        modal.find('#confirm-action').text(confirmButtonText);

        modal.find('#confirm-action').attr('href', url);
        modal.find('.modal-body').html(bodyText);
    }).on('hide.bs.modal', function () {
        const modal = $(this);

        modal.find('.modal-body').html('');
        modal.find('#cancel-action').html('');
        modal.find('#confirm-action').html('');
        modal.find('#confirm-action').attr('href', '');
    });
};

/**
 * Prevent double form submits
 */
document.querySelectorAll('form').forEach((form) => {
    'use strict';

    form.addEventListener('submit', (e) => {
        // Prevent if already submitting
        if (form.classList.contains('is-submitting')) {
            e.preventDefault();
        }

        // Add class to hook our visual indicator on
        form.classList.add('is-submitting');
    });
});
