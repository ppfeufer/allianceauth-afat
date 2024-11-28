/* global afatJsSettingsOverride, afatJsSettingsDefaults */

// Build the settings object
let afatSettings = afatJsSettingsDefaults;
if (typeof afatJsSettingsOverride !== 'undefined') {
    afatSettings = Object.assign(
        {},
        afatJsSettingsDefaults,
        afatJsSettingsOverride
    );
}

/**
 * Datetime format for AFAT
 *
 * @type {string}
 */
const AFAT_DATETIME_FORMAT = afatSettings.datetimeFormat; // eslint-disable-line no-unused-vars

/**
 * Fetch data from an ajax URL
 *
 * @param {string} url The URL to fetch data from
 * @returns {Promise<any>} The fetched data
 */
const fetchAjaxData = async (url) => { // eslint-disable-line no-unused-vars
    'use strict';

    return await fetch(url)
        .then(response => {
            if (response.ok) {
                return Promise.resolve(response);
            } else {
                return Promise.reject(new Error('Failed to load'));
            }
        })
        .then(response => response.json())
        .then(data => {
            return data;
        })
        .catch(function (error) {
            console.log(`Error: ${error.message}`);
        });
};

/**
 * Convert a string to a slug
 * @param {string} text
 * @returns {string}
 */
const convertStringToSlug = (text) => { // eslint-disable-line no-unused-vars
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
const sortTable = (table, order) => { // eslint-disable-line no-unused-vars
    'use strict';

    const asc = order === 'asc';
    const tbody = table.find('tbody');

    tbody.find('tr').sort((a, b) => {
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
const manageModal = (modalElement) => { // eslint-disable-line no-unused-vars
    'use strict';

    /**
     * Set modal buttons
     *
     * @param {string} confirmButtonText
     * @param {string} cancelButtonText
     */
    const setModalButtons = (confirmButtonText, cancelButtonText) => {
        modalElement.find('#confirm-action').text(confirmButtonText);
        modalElement.find('#cancel-action').text(cancelButtonText);
    };

    /**
     * Set modal body
     *
     * @param {string} bodyText
     */
    const setModalBody = (bodyText) => {
        modalElement.find('.modal-body').html(bodyText);
    };

    /**
     * Set modal confirm action
     *
     * @param {string} confirmActionUrl
     */
    const setModalConfirmActionUrl = (confirmActionUrl) => {
        modalElement.find('#confirm-action').attr('href', confirmActionUrl);
    };

    /**
     * Set modal elements
     *
     * @param {string} bodyText
     * @param {string} confirmButtonText
     * @param {string} cancelButtonText
     * @param {string} confirmActionUrl
     */
    const setModalElements = (bodyText, confirmButtonText, cancelButtonText, confirmActionUrl) => {
        setModalButtons(confirmButtonText, cancelButtonText);
        setModalBody(bodyText);
        setModalConfirmActionUrl(confirmActionUrl);
    };

    /**
     * Clear modal elements
     */
    const clearModalElements = () => {
        modalElement.find('.modal-body').html('');
        modalElement.find('#cancel-action').text();
        modalElement.find('#confirm-action').text();
        modalElement.find('#confirm-action').attr('href', '');
    };

    modalElement.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget); // Button that triggered the modal
        const url = button.data('url'); // Extract info from data-url attributes
        const cancelText = button.data('cancel-text');
        const confirmText = button.data('confirm-text');
        const bodyText = button.data('body-text');
        let confirmButtonText = modalElement.find('#confirmButtonDefaultText').text();
        let cancelButtonText = modalElement.find('#cancelButtonDefaultText').text();

        if (typeof cancelText !== 'undefined' && cancelText !== '') {
            cancelButtonText = cancelText;
        }

        if (typeof confirmText !== 'undefined' && confirmText !== '') {
            confirmButtonText = confirmText;
        }

        setModalElements(bodyText, confirmButtonText, cancelButtonText, url);
    }).on('hide.bs.modal', () => {
        clearModalElements();
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
