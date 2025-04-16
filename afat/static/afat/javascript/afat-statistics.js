/* global afatSettings, bootstrap, Chart, fetchAjaxData */

const elementBody = document.querySelector('body');
const elementBodyCss = getComputedStyle(elementBody);

Chart.defaults.color = elementBodyCss.color;

/**
 * Draw a chart on the given element with the given data and options using Chart.js …
 *
 * @param {HTMLElement} element The element to draw the chart on
 * @param {string} chartType The type of chart to draw
 * @param {object} data The data to draw
 * @param {object} options The options to draw the chart with
 */
const drawChart = (element, chartType, data, options) => { // eslint-disable-line no-unused-vars
    'use strict';

    const chart = new Chart(element, { // eslint-disable-line no-unused-vars
        type: chartType,
        data: data,
        options: options
    });
};

$(document).ready(() => {
    'use strict';

    /**
     * Show the given element
     *
     * @param {string} selector Element selector (class or ID)
     */
    const showElement = (selector) => {
        $(selector).removeClass('d-none');
    };

    /**
     * Hide the given element
     *
     * @param {string} selector Element selector (class or ID)
     */
    const hideElement = (selector) => {
        $(selector).addClass('d-none');
    };

    /**
     * Add onClick event to the main character details button
     */
    const addBtnMainCharacterDetailsEvent = () => {
        const btnMainCharacterDetails = $('.btn-afat-corp-stats-view-character');

        if (btnMainCharacterDetails.length > 0) {
            btnMainCharacterDetails.on('click', (event) => {
                const btn = $(event.currentTarget);
                const characterName = btn.data('character-name');
                const url = btn.data('url');

                // Elements to hide initially
                const hideInitially= [
                    '#col-character-alt-characters .afat-character-alt-characters .afat-no-data',
                    '#col-character-alt-characters .afat-character-alt-characters .afat-character-alt-characters-table'
                ];

                hideInitially.forEach(selector => {
                    hideElement(selector);
                });

                // Elements to show initially
                const showInitially = [
                    '#col-character-alt-characters',
                    '#col-character-alt-characters .afat-character-alt-characters .afat-spinner'
                ];

                showInitially.forEach(selector => {
                    showElement(selector);
                });

                // Set the main character name
                $('#afat-corp-stats-main-character-name').text(characterName);

                // Fetch FAT data for all characters of this main character
                fetchAjaxData(url).then(tableData => {
                    const table = $('#character-alt-characters');

                    // If we have table data from the server
                    if (tableData) {
                        // Hide the spinner
                        hideElement('#col-character-alt-characters .afat-character-alt-characters .afat-spinner');

                        // If we have no data
                        if (Object.keys(tableData).length === 0) {
                            // Show the no data message
                            showElement('#col-character-alt-characters .afat-character-alt-characters .afat-no-data');
                        } else {
                            // Show the table
                            showElement('#col-character-alt-characters .afat-character-alt-characters .afat-character-alt-characters-table');

                            // Destroy the table if it already exists
                            if ($.fn.DataTable.isDataTable(table)) {
                                table.DataTable().destroy();
                            }

                            // Create the table
                            table.DataTable({
                                language: afatSettings.dataTable.language,
                                data: tableData,
                                // paging: false,
                                // lengthChange: false,
                                columns: [
                                    { data: 'character_name' },
                                    { data: 'fat_count' },
                                    { data: 'show_details_button' },
                                    { data: 'in_main_corp' },
                                ],
                                order: [
                                    [3, 'desc'],
                                    [1, 'desc'],
                                    [0, 'asc']
                                ],
                                columnDefs: [
                                    {
                                        targets: 1,
                                        createdCell: (td) => {
                                            $(td).addClass('text-end');
                                        }
                                    },
                                    {
                                        targets: 2,
                                        createdCell: (td) => {
                                            $(td).addClass('text-end');
                                        },
                                        sortable: false
                                    },
                                    {
                                        targets: 3,
                                        visible: false
                                    }
                                ]
                            });
                        }
                    }
                }).then(() => {
                    // Show bootstrap tooltips
                    [].slice.call(
                        document.querySelectorAll(
                            '[data-bs-tooltip="afat"]'
                        )
                    ).map((tooltipTriggerEl) => {
                        return new bootstrap.Tooltip(tooltipTriggerEl);
                    });
                }).catch(error => {
                    console.log(`Error: ${error.message}`);
                });
            });
        }
    };

    // Start the script
    (() => {
        addBtnMainCharacterDetailsEvent();
    })();
});
